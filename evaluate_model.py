"""Evaluate the saved model on an unseen, labelled PlantVillage test directory.

Expected layout:
    test_data/
        Apple___Apple_scab/
        Apple___Black_rot/
        ...
        Tomato___healthy/
"""

import argparse
import json
from pathlib import Path

import numpy as np
from keras.applications.vgg19 import preprocess_input
from keras.models import load_model
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from tensorflow.keras.preprocessing.image import ImageDataGenerator

BASE_DIR = Path(__file__).resolve().parent


def dataset_class_name(name):
    return name.replace("Tomato___health", "Tomato___healthy")


def main():
    parser = argparse.ArgumentParser(description="Evaluate the PlantVillage classifier.")
    parser.add_argument(
        "--data-dir",
        default=BASE_DIR / "test_data",
        type=Path,
        help="Directory containing one folder per model class.",
    )
    parser.add_argument("--batch-size", type=int, default=32)
    args = parser.parse_args()

    with (BASE_DIR / "trained_model" / "datafile.json").open(encoding="utf-8") as file:
        class_map = json.load(file)
    class_names = [
        dataset_class_name(class_map[str(index)])
        for index in range(len(class_map))
    ]

    if not args.data_dir.is_dir():
        raise SystemExit(f"Test directory not found: {args.data_dir}")
    missing_classes = [name for name in class_names if not (args.data_dir / name).is_dir()]
    if missing_classes:
        raise SystemExit(
            "The test data is missing model-class folders. First missing folders: "
            + ", ".join(missing_classes[:5])
        )

    generator = ImageDataGenerator(preprocessing_function=preprocess_input).flow_from_directory(
        args.data_dir,
        classes=class_names,
        target_size=(256, 256),
        batch_size=args.batch_size,
        class_mode="sparse",
        shuffle=False,
    )
    if generator.samples == 0:
        raise SystemExit("No test images found.")

    model = load_model(BASE_DIR / "trained_model" / "best_model.h5")
    probabilities = model.predict(generator, verbose=1)
    predicted = np.argmax(probabilities, axis=1)
    actual = generator.classes

    accuracy = accuracy_score(actual, predicted)
    report = classification_report(
        actual, predicted, labels=range(len(class_names)), target_names=class_names,
        zero_division=0, output_dict=True,
    )
    matrix = confusion_matrix(actual, predicted, labels=range(len(class_names))).tolist()
    results = {
        "images_evaluated": int(generator.samples),
        "overall_accuracy": round(float(accuracy), 6),
        "overall_accuracy_percent": round(float(accuracy * 100), 2),
        "classification_report": report,
        "confusion_matrix": matrix,
        "class_order": class_names,
    }
    output_file = BASE_DIR / "evaluation_results.json"
    output_file.write_text(json.dumps(results, indent=2), encoding="utf-8")

    print(f"Images evaluated: {generator.samples}")
    print(f"Overall accuracy: {accuracy * 100:.2f}%")
    print(f"Detailed report saved to: {output_file.name}")


if __name__ == "__main__":
    main()
