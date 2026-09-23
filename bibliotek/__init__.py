"""
Bibliotek for VitnemalOCR - OCR processing utilities for student transcripts.

This package provides utilities for processing student transcripts (vitnemål) using
Mistral AI's OCR capabilities.
"""

# Configuration
from bibliotek.config import (
    create_mistral_client,
    get_docling_url,
)

# PDF utilities
from bibliotek.pdf_utils import (
    pdf_to_base64,
    create_document_url,
)

# OCR processing
from bibliotek.ocr import (
    process_document_ocr,
    process_document_ocr_docling,
)

# File I/O
from bibliotek.file_io import (
    save_json,
)

# Models
from bibliotek.models import (
    Vitnemaldata,
    OcrResultatData,
)

# Document pre-classification (logo/header detection before OCR)
from bibliotek.document_classifier import (
    classify_image,
    classify_pdf_base64,
)

__all__ = [
    # Configuration
    "create_mistral_client",
    "get_docling_url",
    # PDF utilities
    "pdf_to_base64",
    "create_document_url",
    # OCR processing
    "process_document_ocr",
    "process_document_ocr_docling",
    # File I/O
    "save_json",
    # Models
    "Vitnemaldata",
    "OcrResultatData",
    # Document pre-classification
    "classify_image",
    "classify_pdf_base64",
]
