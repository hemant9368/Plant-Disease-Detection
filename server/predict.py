import sys
import os
import json
from keras.models import load_model
import numpy as np
from tensorflow.keras.utils import load_img, img_to_array
from keras.applications.vgg19 import preprocess_input
import pandas as pd

baseDir = os.path.join(os.getcwd(), 'trained_model')
model = load_model(os.path.join(baseDir, 'best_model.h5'))

data = json.load(open(os.path.join(baseDir, 'datafile.json')))
databaseDir = os.path.join(os.getcwd(), 'data_files')
df = pd.read_csv(open(os.path.join(databaseDir, "supplement_info.csv")))

def prediction(path):
    img = load_img(path, target_size=(256, 256))
    i = img_to_array(img)
    im = preprocess_input(i)
    img = np.expand_dims(im, axis=0)
    pred = np.argmax(model.predict(img))
    value = data[str(pred)]
    return df.loc[df['disease_name'] == value].values[0][0]

if __name__ == "__main__":
    image_path = sys.argv[1]
    try:
        result = prediction(image_path)
        response = {
            "product_id": result
        }
    except Exception as e:
        response = {
            "error": str(e)
        }
    
    print(json.dumps(response))
