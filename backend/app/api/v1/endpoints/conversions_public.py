"""Stateless conversion history endpoints for the Morphvert MVP."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.schemas.pdf_conversion import ConversionDetailResponse, ConversionHistoryItem


router = APIRouter(prefix="/conversions", tags=["conversions"])


@router.get("/history", response_model=list[ConversionHistoryItem])
async def conversion_history() -> list[ConversionHistoryItem]:
    """Return an empty history because the MVP does not persist conversion jobs."""
    return []


@router.get("/{conversion_id}", response_model=ConversionDetailResponse)
async def get_conversion_detail(conversion_id: UUID) -> ConversionDetailResponse:
    """Conversion history is not persisted in the lightweight MVP."""
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversion history is not persisted")


@router.delete("/{conversion_id}",
    status_code=status.HTTP_200_OK)
async def delete_conversion(conversion_id: UUID) -> None:
    """No-op delete for compatibility with clients that still call the endpoint."""
    return None
