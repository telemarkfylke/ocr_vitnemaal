"""Classifies a document (image or PDF) using the trained YOLO model, to decide
whether it's worth sending to OCR or routing straight to the manual queue.

    from bibliotek.document_classifier import classify_pdf_base64

    result = classify_pdf_base64(base64_pdf)
    # result = {"Vitnemaal": 0.91, "Hovedprosjekt": 0.62}
    # -> only classes detected above the confidence threshold are included

    if result:
        ... # send to OCR
    else:
        ... # send to manual queue
"""
import base64
from pathlib import Path

import pymupdf as fitz
from PIL import Image
from ultralytics import YOLO
from ultralytics.engine.results import Results

DEFAULT_WEIGHTS = Path(__file__).parent / "best.pt"
PDF_RENDER_DPI = 200  # matches the resolution the training images were rendered at

_model = None


def load_model(weights_path: str | Path = DEFAULT_WEIGHTS) -> YOLO:
    """Loads the model once and caches it, so repeated calls in the same process are fast."""
    global _model
    if _model is None:
        _model = YOLO(str(weights_path))
    return _model


def _detections_from_results(model: YOLO, results: Results) -> dict[str, float]:
    detections: dict[str, float] = {}
    for box in results.boxes:
        class_name = model.names[int(box.cls[0])]
        confidence = float(box.conf[0])
        if confidence > detections.get(class_name, 0.0):
            detections[class_name] = confidence
    return detections


def classify_image(image: str | Path | Image.Image, conf_threshold: float = 0.2, weights_path: str | Path = DEFAULT_WEIGHTS) -> dict[str, float]:
    """Runs the model on a single already-rasterized document image (a file path or a PIL Image).

    Returns a dict of {class_name: confidence} for every class detected with
    confidence >= conf_threshold. If a class is detected multiple times in the
    same image, only the highest confidence is kept. An empty dict means no
    class was confidently detected.
    """
    model = load_model(weights_path)
    source = str(image) if isinstance(image, (str, Path)) else image
    results = model.predict(source=source, conf=conf_threshold, verbose=False)
    return _detections_from_results(model, results[0])


def classify_pdf_base64(
    base64_pdf: str,
    conf_threshold: float = 0.2,
    page_number: int = 0,
    weights_path: str | Path = DEFAULT_WEIGHTS,
) -> dict[str, float]:
    """Renders one page of a base64-encoded PDF to an image and classifies it.

    page_number is 0-indexed; the logo/header the model looks for is expected
    on the first page of these documents.
    """
    pdf_bytes = base64.b64decode(base64_pdf)
    with fitz.open(stream=pdf_bytes, filetype="pdf") as pdf:
        page = pdf[page_number]
        pixmap = page.get_pixmap(dpi=PDF_RENDER_DPI)
        image = Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)

    return classify_image(image, conf_threshold=conf_threshold, weights_path=weights_path)


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python document_classifier.py <path-to-image-or-pdf>")
        sys.exit(1)

    path = Path(sys.argv[1])
    if path.suffix.lower() == ".pdf":
        print(classify_pdf_base64(base64.b64encode(path.read_bytes()).decode("utf-8")))
    else:
        print(classify_image(path))
