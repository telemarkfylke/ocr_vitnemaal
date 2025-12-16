"""
PDF processing utilities.
"""

import base64
from pathlib import Path


def pdf_to_base64(file_path: str | Path) -> str:
    """
    Convert a PDF file to base64 encoded string.

    Args:
        file_path: Path to the PDF file

    Returns:
        Base64 encoded string of the PDF content

    Raises:
        FileNotFoundError: If the file does not exist
        PermissionError: If the file cannot be read
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Filen {file_path} finnes ikke")

    if not path.is_file():
        raise ValueError(f"{file_path} er ikke en fil")

    pdf_bytes = path.read_bytes()
    return base64.b64encode(pdf_bytes).decode("utf-8")


def create_document_url(base64_pdf: str) -> str:
    """
    Create a data URL for a base64 encoded PDF.

    Args:
        base64_pdf: Base64 encoded PDF string

    Returns:
        Data URL string for use with Mistral API
    """
    return f"data:application/pdf;base64,{base64_pdf}"
