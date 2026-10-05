"""Filesystem-backed upload service for the Morphvert MVP."""

from __future__ import annotations

import logging
from io import BytesIO
from pathlib import Path

from fastapi import HTTPException, UploadFile, status

from app.core.config import settings
from app.core.constants import FileType
from app.schemas.schemas import File as FileSchema
from app.storage.file_store import LocalFileStore
from app.utils.file_utils import ensure_upload_directories, infer_file_type, validate_file_upload


logger = logging.getLogger(__name__)


class UploadService:
    """Handle anonymous file uploads with validation and filesystem persistence."""

    def __init__(self, db=None) -> None:
        self.db = db
        self.store = LocalFileStore()

    async def upload_file(self, upload_file: UploadFile) -> FileSchema:
        """Validate, store, and return metadata for an uploaded file."""
        ensure_upload_directories()

        original_filename = upload_file.filename or "file"
        mime_type = upload_file.content_type or ""

        logger.info("upload started filename=%s mime_type=%s", original_filename, mime_type)

        file_bytes = await upload_file.read()
        is_valid, validation_error = validate_file_upload(
            filename=original_filename,
            mime_type=mime_type,
            file_size=len(file_bytes),
        )
        if not is_valid:
            logger.warning("upload rejected filename=%s reason=%s", original_filename, validation_error)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=validation_error)

        self._validate_file_contents(original_filename, file_bytes)

        file_type = infer_file_type(original_filename)
        metadata = self.store.save_bytes(
            content=file_bytes,
            original_filename=original_filename,
            mime_type=mime_type,
            target_directory=Path(settings.LOCAL_STORAGE_PATH),
            file_type=file_type,
            is_converted=False,
            persist_metadata=True,
        )

        logger.info("upload completed file_id=%s filename=%s", metadata.file_id, original_filename)
        return FileSchema(
            id=metadata.file_id,
            filename=metadata.filename,
            description=None,
            tags=[],
            user_id=None,
            file_type=file_type.value,
            mime_type=mime_type,
            file_size=len(file_bytes),
            is_public=False,
            is_converted=False,
            download_count=0,
            created_at=metadata.created_at,
            updated_at=metadata.created_at,
        )

    def _validate_file_contents(self, filename: str, file_bytes: bytes) -> None:
        """Reject obviously corrupted PDFs and images when optional libraries are available."""
        suffix = Path(filename).suffix.lower()

        if suffix == ".pdf":
            try:
                from pypdf import PdfReader
            except ImportError:
                return

            try:
                PdfReader(BytesIO(file_bytes))
            except Exception as exc:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Corrupted PDF file",
                ) from exc

        if suffix in {".jpg", ".jpeg", ".png"}:
            try:
                from PIL import Image
            except ImportError:
                return

            try:
                image = Image.open(BytesIO(file_bytes))
                image.load()
            except Exception as exc:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Corrupted image file",
                ) from exc
