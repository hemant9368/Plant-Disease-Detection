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
MIN_GREEN_RATIO = 0.03
MIN_SUPPORTING_LEAF_COLOR_RATIO = 0.08
MIN_CENTER_GREEN_RATIO = 0.05


class NotPlantImageError(ValueError):
    """Raised when an image has no detectable leaf-like color content."""


def canonical_disease_name(name):
    """Align training labels with the treatment CSV's historic naming."""
    return (
        name.replace("Cherry_(including_sour)", "Cherry")
        .replace("Corn_(maize)", "Corn")
        .replace("Common_rust_", "Common_rust")
        .replace("Tomato___health", "Tomato___healthy")
    )


def has_leaf_like_content(image_array):
    red, green, blue = image_array[..., 0], image_array[..., 1], image_array[..., 2]
    green_leaf = (green > red * 1.02) & (green > blue * 1.05) & (green > 35)
    yellow_leaf = (red > blue * 1.25) & (green > blue * 1.15) & (red > 55) & (green > 45)
    brown_leaf = (
        (red > green * 1.1)
        & (green > red * 0.35)
        & (green > blue * 1.15)
        & (red > 45)
        & (green > 25)
    )
    green_ratio = np.mean(green_leaf)
    supporting_leaf_color_ratio = np.mean(yellow_leaf | brown_leaf)
    height, width = green_leaf.shape
    center = (slice(height // 4, height * 3 // 4), slice(width // 4, width * 3 // 4))
    center_green_ratio = np.mean(green_leaf[center])
    return green_ratio >= MIN_GREEN_RATIO and center_green_ratio >= MIN_CENTER_GREEN_RATIO and (
        green_ratio + supporting_leaf_color_ratio >= MIN_SUPPORTING_LEAF_COLOR_RATIO
    )


def prediction(image_path):
    image = load_img(image_path, target_size=(256, 256))
    image_array = img_to_array(image)
    if not has_leaf_like_content(image_array):
        raise NotPlantImageError("The image does not appear to contain a plant leaf")
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
