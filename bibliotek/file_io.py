"""
File I/O operations for saving and loading data.
"""

import json
from pathlib import Path
from typing import Any


def save_json(data: dict | Any, file_path: str | Path, ensure_ascii: bool = False, indent: int = 4) -> None:
    """
    Save data to a JSON file.

    Args:
        data: Data to save (dict or object with model_dump_json method)
        file_path: Path where the file should be saved
        ensure_ascii: If True, non-ASCII characters are escaped
        indent: Number of spaces for indentation

    Raises:
        OSError: If the file cannot be written
    """
    path = Path(file_path)

    # Create parent directory if it doesn't exist
    path.parent.mkdir(parents=True, exist_ok=True)

    # Handle Pydantic models
    if hasattr(data, 'model_dump_json'):
        with open(path, "w", encoding="utf-8") as f:
            f.write(data.model_dump_json(indent=indent))
    # Handle dict or other JSON-serializable data
    else:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=ensure_ascii, indent=indent)
