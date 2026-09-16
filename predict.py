"""Model loading and treatment-data lookup."""

import json
from pathlib import Path

import numpy as np
import pandas as pd
from keras.applications.vgg19 import preprocess_input
from keras.models import load_model
from tensorflow.keras.utils import img_to_array, load_img

BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "trained_model"

model = load_model(MODEL_DIR / "best_model.h5")
with (MODEL_DIR / "datafile.json").open(encoding="utf-8") as file:
    CLASS_NAMES = json.load(file)
TREATMENTS = pd.read_csv(BASE_DIR / "data_files" / "supplement_info.csv")


def canonical_disease_name(name):
    """Align training labels with the treatment CSV's historic naming."""
    return (
        name.replace("Cherry_(including_sour)", "Cherry")
        .replace("Corn_(maize)", "Corn")
        .replace("Common_rust_", "Common_rust")
        .replace("Tomato___health", "Tomato___healthy")
    )


def prediction(image_path):
    image = load_img(image_path, target_size=(256, 256))
    image_array = img_to_array(image)
    batch = np.expand_dims(preprocess_input(image_array), axis=0)
    probabilities = model.predict(batch, verbose=0)[0]
    class_index = int(np.argmax(probabilities))
    disease_name = canonical_disease_name(CLASS_NAMES[str(class_index)])
    treatment = TREATMENTS.loc[TREATMENTS["disease_name"].eq(disease_name)]
    if treatment.empty:
        raise LookupError(f"No treatment entry configured for {disease_name}")
    return int(treatment.iloc[0]["index"]), disease_name, float(probabilities[class_index])


def getDataFromCSV(product_id):
    if product_id is None:
        return None
    result = TREATMENTS.loc[TREATMENTS["index"].eq(product_id)]
    return None if result.empty else result.iloc[0].to_dict()
