"""
Console Todo Application - Storage Layer

This module handles persistent JSON storage with atomic writes and error handling.
"""

import json
from pathlib import Path
from typing import Optional

from src.models import TaskCollection, StorageError


# Storage file location
STORAGE_FILE = Path("tasks.json")


def load_collection() -> TaskCollection:
    """
    Loads TaskCollection from JSON storage.

    Error handling:
    - Missing file → returns empty collection
    - Corrupted JSON → backs up to .backup, returns empty collection
    - Invalid data → returns empty collection

    Returns:
        TaskCollection instance (empty if file missing or corrupted)
    """
    # Handle missing file
    if not STORAGE_FILE.exists():
        return TaskCollection(next_id=1, tasks=[])

    try:
        # Read and parse JSON
        with STORAGE_FILE.open('r', encoding='utf-8') as f:
            data = json.load(f)

        # Deserialize and return collection
        return TaskCollection.from_dict(data)

    except json.JSONDecodeError as e:
        # Corrupted JSON - backup and return empty
        backup_path = Path("tasks.json.backup")
        try:
            STORAGE_FILE.rename(backup_path)
            print(f"Warning: Corrupted data file backed up to {backup_path}")
        except Exception:
            pass  # If backup fails, continue anyway

        return TaskCollection(next_id=1, tasks=[])

    except Exception as e:
        # Other errors - return empty collection
        print(f"Warning: Failed to load tasks: {e}")
        return TaskCollection(next_id=1, tasks=[])


def save_collection(collection: TaskCollection) -> None:
    """
    Saves TaskCollection to JSON storage with atomic writes.

    Uses atomic write pattern:
    1. Write to temporary file
    2. Rename temp file to final destination (atomic on POSIX)

    Args:
        collection: TaskCollection to save

    Raises:
        StorageError: If save operation fails
    """
    try:
        # Serialize collection
        data = collection.to_dict()

        # Write to temporary file
        temp_path = Path("tasks.json.tmp")
        with temp_path.open('w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        # Atomic rename (replaces existing file)
        temp_path.replace(STORAGE_FILE)

    except PermissionError as e:
        raise StorageError(
            f"Permission denied writing to {STORAGE_FILE}. "
            f"Check file permissions and try again."
        )

    except OSError as e:
        if "disk full" in str(e).lower() or "no space" in str(e).lower():
            raise StorageError(
                f"Disk full. Cannot save tasks. "
                f"Free up space and try again."
            )
        else:
            raise StorageError(f"Failed to save tasks: {e}")

    except Exception as e:
        raise StorageError(f"Unexpected error saving tasks: {e}")
