"""
Bibliotek for VitnemalOCR - OCR processing utilities for student transcripts.

This package provides utilities for processing student transcripts (vitnemål) using
Mistral AI's OCR capabilities.
"""

# Configuration
from bibliotek.config import (
    create_mistral_client,
)

# PDF utilities
from bibliotek.pdf_utils import (
    pdf_to_base64,
    create_document_url,
)

# OCR processing
from bibliotek.ocr import (
    process_document_ocr,
)

# File I/O
from bibliotek.file_io import (
    save_json,
)

# Models
from bibliotek.models import (
    Vitnemaldata,
)

__all__ = [
    # Configuration
    "create_mistral_client",
    # PDF utilities
    "pdf_to_base64",
    "create_document_url",
    # OCR processing
    "process_document_ocr",
    # File I/O
    "save_json",
    # Models
    "Vitnemaldata",
]
