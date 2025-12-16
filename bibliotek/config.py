"""
Configuration management for the transcript OCR application.
"""

import os
import dotenv
from mistralai import Mistral


def load_environment() -> None:
    """Load environment variables from .env file."""
    dotenv.load_dotenv()


def get_api_key() -> str:
    """
    Get the Mistral API key from environment variables.

    Returns:
        API key string

    Raises:
        ValueError: If MISTRAL_API_KEY is not found in environment variables
    """
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        raise ValueError("MISTRAL_API_KEY ikke funnet i miljøvariabler")
    return api_key


def create_mistral_client(api_key: str | None = None) -> Mistral:
    """
    Create and return a Mistral client instance.

    Args:
        api_key: Optional API key. If not provided, will be loaded from environment.

    Returns:
        Mistral client instance
    """
    if api_key is None:
        load_environment()
        api_key = get_api_key()

    return Mistral(api_key=api_key)
