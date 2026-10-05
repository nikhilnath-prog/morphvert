from __future__ import annotations

import logging
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse

from app.storage.file_store import LocalFileStore

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/download", tags=["download"])
store = LocalFileStore()


@router.get("/{file_id}")
async def download_file(file_id: UUID) -> FileResponse:
    metadata = store.load_metadata(file_id)

    if metadata is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )

    file_path = store.resolve_file_path(file_id)

    logger.info(
        "file downloaded file_id=%s path=%s",
        file_id,
        file_path,
    )

    return FileResponse(
        path=str(file_path),
        filename=metadata.original_filename,
        media_type=metadata.mime_type,
    )