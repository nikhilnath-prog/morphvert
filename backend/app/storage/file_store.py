"""Local file storage and metadata registry for the Morphvert MVP."""

from __future__ import annotations

import json
import logging
import mimetypes
from dataclasses import dataclass
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from typing import Optional
from uuid import UUID, uuid4

from fastapi import HTTPException, UploadFile, status

from app.core.config import settings
from app.core.constants import FileType, StorageType
from app.utils.file_utils import ensure_upload_directories, generate_uuid_filename, infer_file_type, validate_file_upload

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class StoredFile:
    """Metadata for a file stored on disk."""

    file_id: UUID
    filename: str
    original_filename: str
    mime_type: str
    file_size: int
    storage_path: Path
    storage_type: StorageType
    file_type: FileType
    is_converted: bool
    created_at: datetime
    updated_at: datetime
    page_number: Optional[int] = None

    def to_metadata(self) -> dict[str, object]:
        return {
            "file_id": str(self.file_id),
            "stored_filename": self.filename,
            "original_filename": self.original_filename,
            "mime_type": self.mime_type,
            "file_size": self.file_size,
            "storage_path": str(self.storage_path),
            "storage_type": self.storage_type.value,
            "file_type": self.file_type.value,
            "is_converted": self.is_converted,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "page_number": self.page_number,
        }


class LocalFileStore:
    """Persist files locally and keep lightweight JSON metadata records."""

    def __init__(self) -> None:
        ensure_upload_directories()
        self.upload_dir = Path(settings.LOCAL_STORAGE_PATH).resolve()
        self.converted_dir = Path(settings.CONVERTED_FILES_PATH).resolve()
        self.temp_dir = Path(settings.TEMP_FILES_PATH).resolve()
        self.logs_dir = Path(settings.LOGS_DIR).resolve()
        self.metadata_dir = self.upload_dir.parent / ".morphvert-metadata"
        self.metadata_dir.mkdir(parents=True, exist_ok=True)

    async def save_upload(self, upload_file: UploadFile) -> StoredFile:
        """Validate and save an uploaded file into the uploads directory."""
        original_filename = upload_file.filename or "file"
        mime_type = upload_file.content_type or mimetypes.guess_type(original_filename)[0] or "application/octet-stream"
        content = await upload_file.read()

        is_valid, validation_error = validate_file_upload(
            filename=original_filename,
            mime_type=mime_type,
            file_size=len(content),
        )
        if not is_valid:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=validation_error)

        self._validate_file_contents(original_filename, content)
        return self.save_bytes(
            content=content,
            original_filename=original_filename,
            mime_type=mime_type,
            target_directory=self.upload_dir,
            file_type=infer_file_type(original_filename),
            is_converted=False,
            persist_metadata=True,
        )

    def save_bytes(
        self,
        *,
        content: bytes,
        original_filename: str,
        mime_type: str,
        target_directory: Path,
        file_type: FileType,
        is_converted: bool,
        storage_type: StorageType = StorageType.LOCAL,
        page_number: Optional[int] = None,
        persist_metadata: bool = True,
        source_file_id: UUID | None = None,
    ) -> StoredFile:
        """Persist raw bytes to disk and optionally persist a JSON metadata manifest."""
        file_id = uuid4()
        stored_filename = generate_uuid_filename(original_filename)
        storage_path = target_directory / stored_filename
        storage_path.parent.mkdir(parents=True, exist_ok=True)

        now = datetime.now(timezone.utc)
        try:
            storage_path.write_bytes(content)
            stored_file = StoredFile(
                file_id=file_id,
                filename=stored_filename,
                original_filename=original_filename,
                mime_type=mime_type,
                file_size=len(content),
                storage_path=storage_path.resolve(),
                storage_type=storage_type,
                file_type=file_type,
                is_converted=is_converted,
                created_at=now,
                updated_at=now,
                page_number=page_number,
            )
            if persist_metadata:
                self._write_metadata(stored_file)
            return stored_file
        except Exception:
            if storage_path.exists():
                storage_path.unlink(missing_ok=True)
            raise

    def register_existing_file(
        self,
        file_path: Path,
        *,
        original_filename: str,
        mime_type: str,
        file_type: FileType,
        is_converted: bool,
        storage_type: StorageType = StorageType.LOCAL,
        page_number: Optional[int] = None,
    ) -> StoredFile:
        """Register a file already written to disk and create metadata for it."""
        resolved_path = self._ensure_safe_path(file_path)
        if not resolved_path.exists():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found on storage")

        file_id = uuid4()
        now = datetime.now(timezone.utc)
        stored_file = StoredFile(
            file_id=file_id,
            filename=resolved_path.name,
            original_filename=original_filename,
            mime_type=mime_type,
            file_size=resolved_path.stat().st_size,
            storage_path=resolved_path,
            storage_type=storage_type,
            file_type=file_type,
            is_converted=is_converted,
            created_at=now,
            updated_at=now,
            page_number=page_number,
        )
        self._write_metadata(stored_file)
        return stored_file

    def load_metadata(self, file_id: UUID) -> Optional[StoredFile]:
        """Load file metadata from disk."""
        metadata_path = self.metadata_dir / f"{file_id}.json"
        if not metadata_path.exists():
            return None

        try:
            payload = json.loads(metadata_path.read_text(encoding="utf-8"))
            storage_path = Path(payload["storage_path"]).resolve()
            return StoredFile(
                file_id=UUID(payload["file_id"]),
                filename=payload.get("stored_filename") or payload.get("filename"),
                original_filename=payload["original_filename"],
                mime_type=payload["mime_type"],
                file_size=int(payload["file_size"]),
                storage_path=storage_path,
                storage_type=StorageType(payload["storage_type"]),
                file_type=FileType(payload["file_type"]),
                is_converted=bool(payload["is_converted"]),
                created_at=datetime.fromisoformat(payload["created_at"]),
                updated_at=datetime.fromisoformat(payload["updated_at"]),
                page_number=payload.get("page_number"),
            )
        except Exception as exc:  # pragma: no cover - corrupt metadata is treated as missing
            logger.warning("Failed to load file metadata: %s", exc)
            return None

    def resolve_file_path(self, file_id: UUID) -> Path:
        """Resolve a file ID to a concrete on-disk path with a secure lookup."""
        metadata = self.load_metadata(file_id)
        if metadata is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

        safe_path = self._ensure_safe_path(metadata.storage_path)
        if not safe_path.exists():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found on storage")

        return safe_path

    def build_download_url(self, file_id: UUID) -> str:
        """Build the public download URL for a stored file."""
        return f"/api/v1/download/{file_id}"

    def _write_metadata(self, stored_file: StoredFile) -> None:
        metadata_path = self.metadata_dir / f"{stored_file.file_id}.json"
        metadata_path.write_text(json.dumps(stored_file.to_metadata(), indent=2), encoding="utf-8")

    def _ensure_safe_path(self, file_path: Path) -> Path:
        resolved = file_path.resolve()
        allowed_roots = [self.upload_dir, self.converted_dir, self.temp_dir]
        if not any(self._is_within_root(resolved, root) for root in allowed_roots):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file path")
        return resolved

    @staticmethod
    def _is_within_root(path: Path, root: Path) -> bool:
        try:
            path.relative_to(root.resolve())
            return True
        except ValueError:
            return False

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


# Singleton store used by endpoints and services.
file_store = LocalFileStore()
