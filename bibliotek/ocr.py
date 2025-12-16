"""
OCR processing functionality using Mistral API.
"""

from typing import Any, Type
from mistralai import Mistral
from mistralai.extra import response_format_from_pydantic_model
from pydantic import BaseModel


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
