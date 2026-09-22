"""
OCR processing functionality using Mistral API and a self-hosted Docling OCR API.
"""

import json
import types
from pathlib import Path
from typing import Any, Type, Union, get_args, get_origin
import requests
from mistralai import Mistral
from mistralai.extra import response_format_from_pydantic_model
from pydantic import BaseModel

from .config import get_docling_url, load_environment


def process_document_ocr(
    client: Mistral,
    document_url: str,
    annotation_model: Type[BaseModel],
    pages: list[int] | None = None,
    include_image_base64: bool = False,
    model: str = "mistral-ocr-latest"
) -> Any:
    """
    Process a document using Mistral OCR API.

    Args:
        client: Mistral client instance
        document_url: Data URL of the document (base64 encoded)
        annotation_model: Pydantic model for document annotations
        pages: List of page indices to process. If None, processes all pages up to 8
        include_image_base64: Whether to include base64 encoded images in response
        model: OCR model to use

    Returns:
        OCR processing response from Mistral API

    Note:
        Document Annotations has a limit of 8 pages. For larger documents,
        consider splitting them into chunks.
    """
    if pages is None:
        pages = list(range(8))

    response = client.ocr.process(
        model=model,
        pages=pages,
        document={
            "type": "document_url",
            "document_url": document_url
        },
        document_annotation_format=response_format_from_pydantic_model(annotation_model),
        include_image_base64=include_image_base64
    )

    return response


_DOCLING_TYPE_NAMES: dict[type, str] = {
    str: "str",
    bool: "bool",
    int: "int",
    float: "float",
}


def _docling_field_type(annotation: Any) -> str:
    """Map a pydantic field annotation to the type name Docling's schema expects."""
    origin = get_origin(annotation)
    if origin in (Union, types.UnionType):
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if len(args) == 1:
            return _docling_field_type(args[0])
    return _DOCLING_TYPE_NAMES.get(annotation, "str")


def _annotation_model_to_docling_schema(annotation_model: Type[BaseModel]) -> list[dict[str, Any]]:
    """Convert a pydantic annotation model to Docling's field schema format."""
    return [
        {
            "name": name,
            "type": _docling_field_type(field.annotation),
            "description": field.description or "",
            "required": field.is_required(),
        }
        for name, field in annotation_model.model_fields.items()
    ]


def process_document_ocr_docling(
    file_path: str | Path,
    annotation_model: Type[BaseModel],
    max_pages: int = 2,
    base_url: str | None = None,
    timeout: int = 120
) -> Any:
    """
    Process a document using a self-hosted Docling OCR API.

    Args:
        file_path: Path to the document to process
        annotation_model: Pydantic model describing the fields to extract
        max_pages: Maximum number of pages to process
        base_url: Docling OCR endpoint URL. If None, loaded from DOCLING_URL
        timeout: Request timeout in seconds

    Returns:
        Parsed JSON response from the Docling OCR API
    """
    if base_url is None:
        load_environment()
        base_url = get_docling_url()

    schema = _annotation_model_to_docling_schema(annotation_model)
    path = Path(file_path)

    with open(path, "rb") as f:
        response = requests.post(
            base_url,
            params={"max_pages": max_pages},
            files={"file": (path.name, f, "application/pdf")},
            data={"schema": json.dumps(schema)},
            timeout=timeout
        )

    response.raise_for_status()
    return response.json()
