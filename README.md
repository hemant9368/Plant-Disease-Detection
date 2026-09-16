# LeafLens — Plant Disease Detection

LeafLens is a Flask web application that classifies a plant-leaf photo with a trained VGG19-based model and presents the matching care/product information. It supports 38 leaf-condition classes from the PlantVillage-style label set.

## Run locally

Use Python 3.9–3.11 in a virtual environment, then install the locked dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open `http://localhost:8001` and upload a JPG or PNG leaf photo. Uploads are limited to 8 MB, verified as images, stored under a random temporary name, and removed immediately after prediction.

For production, use:

```bash
gunicorn app:app
```

## Project structure

- `app.py` — Flask routes, upload validation, and UI rendering.
- `predict.py` — model inference and label-to-treatment lookup.
- `trained_model/` — the saved model and its class-index mapping.
- `data_files/supplement_info.csv` — treatment/product metadata.
- `templates/` and `static/` — responsive web interface.

`client/` and `server/` are legacy React/Express prototypes and are not used by the supported Flask application. Do not run them alongside Flask on port 8001.

## Important limitations

- A classifier’s confidence is not a diagnosis. Retake unclear photos and confirm important treatment decisions with a local agricultural extension worker or qualified expert.
- Product suggestions are data entries, not endorsements. Always check crop registration, label instructions, dosage, protective equipment, and local regulations before use.
- Keep `trained_model/datafile.json` and `data_files/supplement_info.csv` aligned. The prediction code normalizes the historic Cherry, Corn, and Tomato naming differences, but any new class must have a matching CSV row.

## Development improvements to consider

- Add automated API, mapping, and browser tests.
- Record model version, training-data source, per-class evaluation metrics, and a confidence threshold before deploying to real users.
- Replace product links with expert-reviewed, region-aware integrated pest-management guidance.
