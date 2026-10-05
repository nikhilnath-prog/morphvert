"""File upload API endpoints for the MVP."""

from fastapi import APIRouter, File as FileType, UploadFile, status

from app.schemas.schemas import File as FileSchema
from app.services.upload_service import UploadService


router = APIRouter(prefix="/files", tags=["files"])


@router.post("/upload", response_model=FileSchema, status_code=status.HTTP_201_CREATED)
async def upload_file(file: UploadFile = FileType(...)) -> FileSchema:
    """Upload a file anonymously and store its metadata on disk."""
    service = UploadService()
    return await service.upload_file(file)
