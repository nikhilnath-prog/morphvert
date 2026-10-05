"""Schemas for PDF conversion workflows.

These models keep the conversion module isolated from route logic and
describe the public request and response payloads used by the MVP endpoints.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class PDFConversionBase(BaseModel):
    """Shared fields for PDF conversion requests."""

    keep_original: bool = Field(default=True, description="Preserve the uploaded source file.")


class PDFToDocxResponse(BaseModel):
    """Response returned after a PDF to DOCX conversion."""

    conversion_id: UUID
    input_file_id: UUID
    output_file_id: UUID
    output_filename: str
    download_url: str
    status: str
    processing_time_ms: int
    created_at: datetime

    class Config:
        from_attributes = True


class PDFToExcelResponse(BaseModel):
    """Response returned after a PDF to XLSX conversion."""

    conversion_id: UUID
    input_file_id: UUID
    output_file_id: UUID
    output_filename: str
    download_url: str
    status: str
    processing_time_ms: int
    created_at: datetime

    class Config:
        from_attributes = True


class ExcelToPDFResponse(BaseModel):
    """Response returned after an XLSX to PDF conversion."""

    conversion_id: UUID
    input_file_id: UUID
    output_file_id: UUID
    output_filename: str
    download_url: str
    status: str
    processing_time_ms: int
    created_at: datetime

    class Config:
        from_attributes = True


class PDFToImagesResponse(BaseModel):
    """Response returned after converting a PDF into page images."""

    conversion_id: UUID
    input_file_id: UUID
    output_file_ids: List[UUID]
    output_filenames: List[str]
    download_urls: List[str]
    status: str
    processing_time_ms: int
    created_at: datetime

    class Config:
        from_attributes = True


class PDFMergeRequest(BaseModel):
    """Request payload for merging multiple PDFs."""

    file_ids: List[UUID] = Field(..., min_length=2, description="Two or more PDF file IDs.")


class PDFMergeResponse(BaseModel):
    """Response returned after merging PDFs."""

    conversion_id: UUID
    input_file_ids: List[UUID]
    output_file_id: UUID
    output_filename: str
    download_url: str
    status: str
    processing_time_ms: int
    created_at: datetime

    class Config:
        from_attributes = True


class PDFSplitRequest(BaseModel):
    """Request payload for splitting a PDF."""

    file_id: UUID


class SplitFileItem(BaseModel):
    """Metadata for a single file produced by a split operation."""

    file_id: UUID
    filename: str
    download_url: str
    page_number: int


class PDFSplitResponse(BaseModel):
    """Response returned after splitting a PDF."""

    conversion_id: UUID
    input_file_id: UUID
    output_files: List[SplitFileItem]
    status: str
    processing_time_ms: int
    created_at: datetime

    class Config:
        from_attributes = True


class ImageToPDFResponse(BaseModel):
    """Response returned after converting a single image into a PDF."""

    conversion_id: UUID
    input_file_id: UUID
    output_file_id: UUID
    output_filename: str
    download_url: str
    status: str
    processing_time_ms: int
    created_at: datetime

    class Config:
        from_attributes = True


class ImagesToPDFResponse(BaseModel):
    """Response returned after merging multiple images into a single PDF."""

    conversion_id: UUID
    input_file_ids: List[UUID]
    output_file_id: UUID
    output_filename: str
    download_url: str
    status: str
    processing_time_ms: int
    created_at: datetime

    class Config:
        from_attributes = True


class PDFCompressResponse(BaseModel):
    """Response returned after compressing a PDF file."""

    conversion_id: UUID
    input_file_id: UUID
    output_file_id: UUID
    output_filename: str
    download_url: str
    status: str
    processing_time_ms: int
    original_size_bytes: int
    compressed_size_bytes: int
    compression_percentage: float
    created_at: datetime

    class Config:
        from_attributes = True


class ConversionStatusResponse(BaseModel):
    """Generic conversion status payload for polling and history views."""

    id: UUID
    conversion_type: str
    status: str
    input_file_id: UUID
    output_file_id: Optional[UUID] = None
    error_message: Optional[str] = None
    processing_time_ms: Optional[int] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ConversionHistoryItem(BaseModel):
    """Lightweight history row for listing conversions."""

    id: UUID
    conversion_type: str
    status: str
    input_file_id: UUID
    input_filename: Optional[str] = None
    output_file_id: Optional[UUID] = None
    output_filename: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ConversionDetailResponse(BaseModel):
    """Detailed conversion response for a single conversion record."""

    id: UUID
    conversion_type: str
    status: str
    input_file_id: UUID
    input_filename: Optional[str] = None
    output_file_id: Optional[UUID] = None
    output_filename: Optional[str] = None
    error_message: Optional[str] = None
    processing_time_ms: Optional[int] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True