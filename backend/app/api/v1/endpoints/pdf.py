"""Public PDF conversion endpoints for the Morphvert MVP."""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from time import perf_counter
from uuid import UUID, uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.converters.pdf_tools import (
    compress_pdf,
    convert_excel_to_pdf,
    convert_image_to_pdf as convert_image_to_pdf_file,
    convert_images_to_pdf as convert_images_to_pdf_file,
    convert_pdf_to_docx,
    convert_pdf_to_excel,
    convert_pdf_to_images,
    ensure_excel_bytes,
    ensure_pdf_bytes,
    merge_pdfs,
    split_pdf as split_pdf_file,
)
from app.core.config import settings
from app.core.constants import FileType
from app.schemas.pdf_conversion import (
    ExcelToPDFResponse,
    ImageToPDFResponse,
    ImagesToPDFResponse,
    PDFCompressResponse,
    PDFMergeResponse,
    PDFSplitResponse,
    PDFToDocxResponse,
    PDFToExcelResponse,
    PDFToImagesResponse,
    SplitFileItem,
)
from app.storage.file_store import LocalFileStore
from app.utils.file_utils import ensure_upload_directories, validate_file_upload


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/convert", tags=["pdf-conversion"])
pdf_router = APIRouter(prefix="/pdf", tags=["pdf-operations"])
store = LocalFileStore()


def _write_temp_input(original_name: str, content_type: str, content: bytes) -> tuple[UUID, Path]:
    suffix = Path(original_name).suffix.lower()
    if suffix == ".pdf":
        file_type = FileType.PDF
    elif suffix == ".xlsx":
        file_type = FileType.XLSX
    elif suffix == ".docx":
        file_type = FileType.DOCX
    else:
        file_type = FileType.PNG

    temp_record = store.save_bytes(
        content=content,
        original_filename=original_name or "input.pdf",
        mime_type=content_type or "application/octet-stream",
        target_directory=store.temp_dir,
        file_type=file_type,
        is_converted=False,
        persist_metadata=False,
    )
    return temp_record.file_id, Path(temp_record.storage_path)

def _register_output(
    *,
    path: Path,
    original_filename: str,
    mime_type: str,
    file_type: FileType,
    source_file_id: UUID | None = None,
    page_number: int | None = None,
) -> UUID:
    return store.register_existing_file(
        file_path=path,
        original_filename=original_filename,
        mime_type=mime_type,
        file_type=file_type,
        is_converted=True,
        page_number=page_number,
    ).file_id


@router.post("/pdf/to-docx", response_model=PDFToDocxResponse, status_code=status.HTTP_201_CREATED)
async def convert_pdf_to_docx_endpoint(file: UploadFile = File(...)) -> PDFToDocxResponse:
    """Convert an uploaded PDF to DOCX and return a download link."""
    ensure_upload_directories()
    started_at = perf_counter()

    original_name = file.filename or ""
    content_type = file.content_type or "application/pdf"
    file_bytes = await file.read()
    ensure_pdf_bytes(original_name, content_type, file_bytes)

    input_file_id, input_path = _write_temp_input(original_name, content_type, file_bytes)
    output_filename = f"{uuid4().hex}.docx"
    output_path = Path(settings.CONVERTED_FILES_PATH) / output_filename
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        convert_pdf_to_docx(input_path, output_path)
    finally:
        input_path.unlink(missing_ok=True)

    output_file_id = _register_output(
        path=output_path,
        original_filename=Path(original_name).stem + ".docx",
        mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        file_type=FileType.DOCX,
        source_file_id=input_file_id,
    )

    now = datetime.utcnow()
    logger.info("conversion completed type=pdf-to-docx output_file_id=%s", output_file_id)
    return PDFToDocxResponse(
        conversion_id=uuid4(),
        input_file_id=input_file_id,
        output_file_id=output_file_id,
        output_filename=output_filename,
        download_url=store.build_download_url(output_file_id),
        status="completed",
        processing_time_ms=int((perf_counter() - started_at) * 1000),
        created_at=now,
    )


@router.post("/pdf/to-excel", response_model=PDFToExcelResponse, status_code=status.HTTP_201_CREATED)
async def convert_pdf_to_excel_endpoint(file: UploadFile = File(...)) -> PDFToExcelResponse:
    """Convert an uploaded PDF into an XLSX workbook using table-friendly text extraction."""
    ensure_upload_directories()
    started_at = perf_counter()

    original_name = file.filename or ""
    content_type = file.content_type or "application/pdf"
    file_bytes = await file.read()

    validate_ok, validation_error = validate_file_upload(
        filename=original_name,
        mime_type=content_type,
        file_size=len(file_bytes),
        allowed_mime_types={"application/pdf"},
        allowed_extensions={".pdf"},
    )
    if not validate_ok:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=validation_error)
    ensure_pdf_bytes(original_name, content_type, file_bytes)

    input_file_id, input_path = _write_temp_input(original_name, content_type, file_bytes)
    output_filename = f"{uuid4().hex}.xlsx"
    output_path = Path(settings.CONVERTED_FILES_PATH) / output_filename
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        convert_pdf_to_excel(input_path, output_path)
    finally:
        input_path.unlink(missing_ok=True)

    output_file_id = _register_output(
        path=output_path,
        original_filename=Path(original_name).stem + ".xlsx",
        mime_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        file_type=FileType.XLSX,
        source_file_id=input_file_id,
    )

    now = datetime.utcnow()
    logger.info("conversion completed type=pdf-to-excel output_file_id=%s", output_file_id)
    return PDFToExcelResponse(
        conversion_id=uuid4(),
        input_file_id=input_file_id,
        output_file_id=output_file_id,
        output_filename=output_filename,
        download_url=store.build_download_url(output_file_id),
        status="completed",
        processing_time_ms=int((perf_counter() - started_at) * 1000),
        created_at=now,
    )


@router.post("/pdf/to-images", response_model=PDFToImagesResponse, status_code=status.HTTP_201_CREATED)
async def convert_pdf_to_images_endpoint(file: UploadFile = File(...)) -> PDFToImagesResponse:
    """Convert an uploaded PDF into PNG page images and return their download URLs."""
    ensure_upload_directories()
    started_at = perf_counter()

    original_name = file.filename or ""
    content_type = file.content_type or "application/pdf"
    file_bytes = await file.read()
    ensure_pdf_bytes(original_name, content_type, file_bytes)

    input_file_id, input_path = _write_temp_input(original_name, content_type, file_bytes)
    output_directory = Path(settings.CONVERTED_FILES_PATH) / uuid4().hex
    output_directory.mkdir(parents=True, exist_ok=True)

    output_file_ids: list[UUID] = []
    output_filenames: list[str] = []
    download_urls: list[str] = []

    try:
        output_paths = convert_pdf_to_images(file_bytes, output_directory)
        for page_number, output_path in enumerate(output_paths, start=1):
            output_file_id = _register_output(
                path=output_path,
                original_filename=output_path.name,
                mime_type="image/png",
                file_type=FileType.PNG,
                source_file_id=input_file_id,
                page_number=page_number,
            )
            output_file_ids.append(output_file_id)
            output_filenames.append(output_path.name)
            download_urls.append(store.build_download_url(output_file_id))
    finally:
        input_path.unlink(missing_ok=True)

    now = datetime.utcnow()
    return PDFToImagesResponse(
        conversion_id=uuid4(),
        input_file_id=input_file_id,
        output_file_ids=output_file_ids,
        output_filenames=output_filenames,
        download_urls=download_urls,
        status="completed",
        processing_time_ms=int((perf_counter() - started_at) * 1000),
        created_at=now,
    )


@router.post("/excel/to-pdf", response_model=ExcelToPDFResponse, status_code=status.HTTP_201_CREATED)
async def convert_excel_to_pdf_endpoint(file: UploadFile = File(...)) -> ExcelToPDFResponse:
    """Convert a spreadsheet workbook into a readable PDF."""
    ensure_upload_directories()
    started_at = perf_counter()

    original_name = file.filename or ""
    content_type = file.content_type or "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    file_bytes = await file.read()

    validate_ok, validation_error = validate_file_upload(
        filename=original_name,
        mime_type=content_type,
        file_size=len(file_bytes),
        allowed_mime_types={"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"},
        allowed_extensions={".xlsx"},
    )
    if not validate_ok:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=validation_error)
    ensure_excel_bytes(original_name, content_type, file_bytes)

    input_file_id, input_path = _write_temp_input(original_name, content_type, file_bytes)
    output_filename = f"{uuid4().hex}.pdf"
    output_path = Path(settings.CONVERTED_FILES_PATH) / output_filename
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        convert_excel_to_pdf(input_path, output_path)
    finally:
        input_path.unlink(missing_ok=True)

    output_file_id = _register_output(
        path=output_path,
        original_filename=Path(original_name).stem + ".pdf",
        mime_type="application/pdf",
        file_type=FileType.PDF,
        source_file_id=input_file_id,
    )

    now = datetime.utcnow()
    logger.info("conversion completed type=excel-to-pdf output_file_id=%s", output_file_id)
    return ExcelToPDFResponse(
        conversion_id=uuid4(),
        input_file_id=input_file_id,
        output_file_id=output_file_id,
        output_filename=output_filename,
        download_url=store.build_download_url(output_file_id),
        status="completed",
        processing_time_ms=int((perf_counter() - started_at) * 1000),
        created_at=now,
    )


@pdf_router.post("/merge", response_model=PDFMergeResponse, status_code=status.HTTP_201_CREATED)
async def merge_pdf(files: list[UploadFile] = File(...)) -> PDFMergeResponse:
    """Merge multiple PDFs into one output PDF."""
    ensure_upload_directories()

    if len(files) < 2:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="At least two PDF files are required")

    started_at = perf_counter()
    input_file_ids: list[UUID] = []
    temp_paths: list[Path] = []

    for upload_file in files:
        original_name = upload_file.filename or ""
        content_type = upload_file.content_type or "application/pdf"
        file_bytes = await upload_file.read()
        ensure_pdf_bytes(original_name, content_type, file_bytes)

        temp_file_id, temp_path = _write_temp_input(original_name, content_type, file_bytes)
        input_file_ids.append(temp_file_id)
        temp_paths.append(temp_path)

    output_filename = f"{uuid4().hex}_merged.pdf"
    output_path = Path(settings.CONVERTED_FILES_PATH) / output_filename
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        merge_pdfs(temp_paths, output_path)
    finally:
        for temp_path in temp_paths:
            temp_path.unlink(missing_ok=True)

    output_file_id = _register_output(
        path=output_path,
        original_filename="merged.pdf",
        mime_type="application/pdf",
        file_type=FileType.PDF,
        source_file_id=input_file_ids[0],
    )

    now = datetime.utcnow()
    return PDFMergeResponse(
        conversion_id=uuid4(),
        input_file_ids=input_file_ids,
        output_file_id=output_file_id,
        output_filename=output_filename,
        download_url=store.build_download_url(output_file_id),
        status="completed",
        processing_time_ms=int((perf_counter() - started_at) * 1000),
        created_at=now,
    )


@pdf_router.post("/split", response_model=PDFSplitResponse, status_code=status.HTTP_201_CREATED)
async def split_pdf_endpoint(file: UploadFile = File(...)) -> PDFSplitResponse:
    """Split a PDF into one file per page and return their download URLs."""
    ensure_upload_directories()
    started_at = perf_counter()

    original_name = file.filename or ""
    content_type = file.content_type or "application/pdf"
    file_bytes = await file.read()
    ensure_pdf_bytes(original_name, content_type, file_bytes)

    input_file_id, input_path = _write_temp_input(original_name, content_type, file_bytes)
    output_directory = Path(settings.CONVERTED_FILES_PATH) / uuid4().hex
    output_directory.mkdir(parents=True, exist_ok=True)

    output_items: list[SplitFileItem] = []

    try:
        output_paths = split_pdf_file(input_path, output_directory)
        for page_number, output_path in enumerate(output_paths, start=1):
            output_file_id = _register_output(
                path=output_path,
                original_filename=f"page_{page_number}.pdf",
                mime_type="application/pdf",
                file_type=FileType.PDF,
                source_file_id=input_file_id,
                page_number=page_number,
            )
            output_items.append(
                SplitFileItem(
                    file_id=output_file_id,
                    filename=output_path.name,
                    download_url=store.build_download_url(output_file_id),
                    page_number=page_number,
                )
            )
    finally:
        input_path.unlink(missing_ok=True)

    now = datetime.utcnow()
    return PDFSplitResponse(
        conversion_id=uuid4(),
        input_file_id=input_file_id,
        output_files=output_items,
        status="completed",
        processing_time_ms=int((perf_counter() - started_at) * 1000),
        created_at=now,
    )


@router.post("/image/to-pdf", response_model=ImageToPDFResponse, status_code=status.HTTP_201_CREATED)
async def convert_image_to_pdf_endpoint(file: UploadFile = File(...)) -> ImageToPDFResponse:
    """Convert a single JPG/PNG image to PDF."""
    ensure_upload_directories()
    started_at = perf_counter()

    original_name = file.filename or ""
    content_type = file.content_type or ""
    file_bytes = await file.read()

    allowed_extensions = {".jpg", ".jpeg", ".png"}
    allowed_mime_types = {"image/jpeg", "image/png"}
    is_valid, validation_error = validate_file_upload(
        filename=original_name,
        mime_type=content_type,
        file_size=len(file_bytes),
        allowed_mime_types=allowed_mime_types,
        allowed_extensions=allowed_extensions,
    )
    if not is_valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=validation_error)

    input_file_id, input_path = _write_temp_input(original_name, content_type, file_bytes)
    output_filename = f"{uuid4().hex}.pdf"
    output_path = Path(settings.CONVERTED_FILES_PATH) / output_filename
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        convert_image_to_pdf_file(file_bytes, output_path)
    finally:
        input_path.unlink(missing_ok=True)

    output_file_id = _register_output(
        path=output_path,
        original_filename=output_filename,
        mime_type="application/pdf",
        file_type=FileType.PDF,
        source_file_id=input_file_id,
    )

    now = datetime.utcnow()
    return ImageToPDFResponse(
        conversion_id=uuid4(),
        input_file_id=input_file_id,
        output_file_id=output_file_id,
        output_filename=output_filename,
        download_url=store.build_download_url(output_file_id),
        status="completed",
        processing_time_ms=int((perf_counter() - started_at) * 1000),
        created_at=now,
    )


@router.post("/images/to-pdf", response_model=ImagesToPDFResponse, status_code=status.HTTP_201_CREATED)
async def convert_images_to_pdf_endpoint(files: list[UploadFile] = File(...)) -> ImagesToPDFResponse:
    """Merge multiple images into a single PDF."""
    ensure_upload_directories()

    if len(files) < 2:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="At least two images are required")

    started_at = perf_counter()
    input_file_ids: list[UUID] = []
    temp_paths: list[Path] = []
    image_bytes_list: list[bytes] = []

    for upload_file in files:
        original_name = upload_file.filename or ""
        content_type = upload_file.content_type or ""
        file_bytes = await upload_file.read()

        allowed_extensions = {".jpg", ".jpeg", ".png"}
        allowed_mime_types = {"image/jpeg", "image/png"}
        is_valid, validation_error = validate_file_upload(
            filename=original_name,
            mime_type=content_type,
            file_size=len(file_bytes),
            allowed_mime_types=allowed_mime_types,
            allowed_extensions=allowed_extensions,
        )
        if not is_valid:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=validation_error)

        temp_file_id, temp_path = _write_temp_input(original_name, content_type, file_bytes)
        input_file_ids.append(temp_file_id)
        temp_paths.append(temp_path)
        image_bytes_list.append(file_bytes)

    output_filename = f"{uuid4().hex}.pdf"
    output_path = Path(settings.CONVERTED_FILES_PATH) / output_filename
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        convert_images_to_pdf_file(image_bytes_list, output_path)
    finally:
        for temp_path in temp_paths:
            temp_path.unlink(missing_ok=True)

    output_file_id = _register_output(
        path=output_path,
        original_filename=output_filename,
        mime_type="application/pdf",
        file_type=FileType.PDF,
        source_file_id=input_file_ids[0],
    )

    now = datetime.utcnow()
    return ImagesToPDFResponse(
        conversion_id=uuid4(),
        input_file_ids=input_file_ids,
        output_file_id=output_file_id,
        output_filename=output_filename,
        download_url=store.build_download_url(output_file_id),
        status="completed",
        processing_time_ms=int((perf_counter() - started_at) * 1000),
        created_at=now,
    )


@pdf_router.post("/compress", response_model=PDFCompressResponse, status_code=status.HTTP_201_CREATED)
async def compress_pdf_endpoint(file: UploadFile = File(...)) -> PDFCompressResponse:
    """Compress a PDF file and return the resulting download URL."""
    ensure_upload_directories()
    started_at = perf_counter()

    original_name = file.filename or ""
    content_type = file.content_type or "application/pdf"
    file_bytes = await file.read()
    ensure_pdf_bytes(original_name, content_type, file_bytes)

    input_file_id, input_path = _write_temp_input(original_name, content_type, file_bytes)
    output_filename = f"{uuid4().hex}_compressed.pdf"
    output_path = Path(settings.CONVERTED_FILES_PATH) / output_filename
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        compress_pdf(input_path, output_path)
    finally:
        input_path.unlink(missing_ok=True)

    output_file_id = _register_output(
        path=output_path,
        original_filename=output_filename,
        mime_type="application/pdf",
        file_type=FileType.PDF,
        source_file_id=input_file_id,
    )

    original_size_bytes = len(file_bytes)
    compressed_size_bytes = output_path.stat().st_size
    compression_percentage = round(((original_size_bytes - compressed_size_bytes) / max(original_size_bytes, 1)) * 100, 2)
    now = datetime.utcnow()

    return PDFCompressResponse(
        conversion_id=uuid4(),
        input_file_id=input_file_id,
        output_file_id=output_file_id,
        output_filename=output_filename,
        download_url=store.build_download_url(output_file_id),
        status="completed",
        processing_time_ms=int((perf_counter() - started_at) * 1000),
        original_size_bytes=original_size_bytes,
        compressed_size_bytes=compressed_size_bytes,
        compression_percentage=compression_percentage,
        created_at=now,
    )
