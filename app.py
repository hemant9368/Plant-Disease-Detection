#!/usr/bin/env python3
"""Flask application for plant disease analysis."""

import os
import uuid
from pathlib import Path

from flask import Flask, jsonify, render_template, request, url_for
from PIL import Image, UnidentifiedImageError
from werkzeug.utils import secure_filename

from predict import NotPlantImageError, getDataFromCSV, prediction

BASE_DIR = Path(__file__).resolve().parent
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

app = Flask(__name__)
app.config.update(
    UPLOAD_FOLDER=BASE_DIR / "images",
    MAX_CONTENT_LENGTH=8 * 1024 * 1024,
)
app.config["UPLOAD_FOLDER"].mkdir(exist_ok=True)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.errorhandler(413)
def file_too_large(_error):
    return jsonify({"error": "Image is too large. Please upload a file under 8 MB."}), 413


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/result")
def result():
    product_id = request.args.get("id", type=int)
    confidence = request.args.get("confidence", type=float)
    app_data = getDataFromCSV(product_id) if product_id is not None else None
    return render_template("result.html", app_data=app_data, confidence=confidence)


@app.route("/analyze", methods=["POST"])
def analyze():
    file = request.files.get("file")
    if file is None or not file.filename:
        return jsonify({
            "error": "Choose a plant image before analysing.",
            "received_fields": sorted(request.form.keys()),
        }), 400
    if not allowed_file(file.filename):
        return jsonify({"error": "Please upload a PNG or JPG image."}), 400

    try:
        image = Image.open(file.stream)
        image.verify()
        file.stream.seek(0)
    except (UnidentifiedImageError, OSError):
        return jsonify({"error": "That file is not a valid image."}), 400

    extension = Path(secure_filename(file.filename)).suffix.lower()
    upload_path = app.config["UPLOAD_FOLDER"] / f"{uuid.uuid4().hex}{extension}"
    file.save(upload_path)
    try:
        product_id, disease_name, confidence = prediction(upload_path)
    except NotPlantImageError as error:
        return jsonify({"error": f"{error}. Please upload a clear photo of a plant leaf."}), 422
    except Exception:
        app.logger.exception("Prediction failed")
        return jsonify({"error": "We could not analyse that image. Please try another clear leaf photo."}), 500
    finally:
        upload_path.unlink(missing_ok=True)

    return jsonify({
        "product_id": product_id,
        "disease_name": disease_name,
        "confidence": round(confidence * 100, 1),
        "result_url": url_for(
            "result",
            id=product_id,
            confidence=round(confidence * 100, 1),
        ),
    })


if __name__ == "__main__":
    from waitress import serve

    serve(app, host="0.0.0.0", port=int(os.getenv("PORT", "8001")))
