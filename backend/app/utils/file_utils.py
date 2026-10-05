"""
Utility functions for file validation, hashing, and common operations.

Includes:
- File validation
- File path utilities
- Checksum calculation
- MIME type validation
"""

import hashlib
import os
from pathlib import Path
from typing import Optional, Sequence, Tuple
from uuid import uuid4

from app.core.config import settings
from app.core.constants import FileType, UPLOAD_ALLOWED_EXTENSIONS, UPLOAD_ALLOWED_MIME_TYPES


def validate_file_upload(
    filename: str,
    mime_type: str,
    file_size: int,
    allowed_mime_types: Optional[Sequence[str]] = None,
    allowed_extensions: Optional[Sequence[str]] = None,
) -> Tuple[bool, str]:
    """
    Validate uploaded file.
    
    Args:
        filename: Original filename
        mime_type: File MIME type
        file_size: File size in bytes
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Validate file size
    if file_size > settings.MAX_FILE_SIZE:
        return False, f"File exceeds maximum size of {settings.MAX_FILE_SIZE} bytes"
    
    # Validate MIME type
    mime_allowlist = set(allowed_mime_types or UPLOAD_ALLOWED_MIME_TYPES.values())
    if mime_type not in mime_allowlist:
        return False, f"MIME type {mime_type} not allowed"
    
    # Validate file extension
    extension = Path(filename).suffix.lower()
    extension_allowlist = set(allowed_extensions or UPLOAD_ALLOWED_EXTENSIONS)
    if extension not in extension_allowlist:
        return False, f"File extension {extension} not allowed"
    
    return True, ""


def infer_file_type(filename: str) -> FileType:
    """Infer the FileType enum from a filename extension."""

    extension = Path(filename).suffix.lower()

    extension_to_file_type = {
        ".pdf": FileType.PDF,
        ".docx": FileType.DOCX,
        ".xlsx": FileType.XLSX,
        ".jpg": FileType.JPG,
        ".jpeg": FileType.JPG,
        ".png": FileType.PNG,
        ".txt": FileType.TXT,
        ".json": FileType.JSON,
    }

    try:
        return extension_to_file_type[extension]
    except KeyError:
        raise ValueError(
            f"Unsupported file extension: {extension}"
        )


def generate_uuid_filename(original_filename: str) -> str:
    """Generate a safe UUID-based filename while preserving the extension."""
    extension = Path(original_filename).suffix.lower()
    return f"{uuid4().hex}{extension}"


def calculate_file_checksum(filepath: str, algorithm: str = "sha256") -> str:
    """
    Calculate file checksum.
    
    Args:
        filepath: Path to file
        algorithm: Hash algorithm (sha256, md5, etc.)
        
    Returns:
        Hex digest of file
    """
    hash_obj = hashlib.new(algorithm)
    
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_obj.update(chunk)
    
    return hash_obj.hexdigest()


def get_safe_filename(user_id: str, original_filename: str) -> str:
    """
    Generate safe filename for storage.
    
    Args:
        user_id: User ID
        original_filename: Original filename
        
    Returns:
        Safe filename with user directory
    """
    import uuid
    
    # Remove path components
    safe_name = os.path.basename(original_filename)
    
    # Add UUID prefix for uniqueness
    name, ext = os.path.splitext(safe_name)
    unique_name = f"{uuid.uuid4().hex[:8]}_{name}{ext}"
    
    return f"{user_id}/{unique_name}"


def cleanup_temp_files() -> int:
    """
    Clean up temporary files that have expired.
    
    Returns:
        Number of files deleted
    """
    import datetime
    import shutil
    
    deleted_count = 0
    temp_dir = Path(settings.TEMP_FILES_PATH)
    
    if not temp_dir.exists():
        return 0
    
    now = datetime.datetime.utcnow()
    
    for file_path in temp_dir.glob("*"):
        if file_path.is_file():
            # Check file age
            file_age = now - datetime.datetime.fromtimestamp(
                file_path.stat().st_mtime
            )
            
            # Delete if older than 24 hours
            if file_age.days >= 1:
                try:
                    file_path.unlink()
                    deleted_count += 1
                except Exception:
                    pass
    
    return deleted_count


def ensure_upload_directories() -> None:
    """Ensure all upload directories exist."""
    paths = {
        "LOCAL_STORAGE_PATH": settings.LOCAL_STORAGE_PATH,
        "CONVERTED_FILES_PATH": settings.CONVERTED_FILES_PATH,
        "TEMP_FILES_PATH": settings.TEMP_FILES_PATH,
        "LOGS_DIR": settings.LOGS_DIR,
    }

    for key, path in paths.items():
        try:
            os.makedirs(path, exist_ok=True)
        except PermissionError:
            # Fallback to app-local directory when the configured path is not writable
            project_root = Path(__file__).resolve().parents[2]
            fallback_dir = project_root / Path(path).name
            try:
                os.makedirs(fallback_dir, exist_ok=True)
            except Exception:
                # As a last resort, try a temp directory
                import tempfile

                fallback_dir = Path(tempfile.mkdtemp(prefix="morphvert_"))

            # Update the runtime setting so other code uses the writable path
            setattr(settings, key, str(fallback_dir))
            # Ensure the rest of the loop uses the fallback
            paths[key] = str(fallback_dir)
