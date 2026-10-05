"""
Conversion API endpoints.

Includes:
- Create conversion job
- Get conversion status
- List user conversions
- Cancel conversion
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.models.models import User
from app.schemas.schemas import (
    Conversion,
    ConversionCreate,
    ConversionDetail,
    PaginatedResponse,
)
from app.core.dependencies import get_current_user
from app.services.services import ConversionService


router = APIRouter(prefix="/conversions", tags=["conversions"])


@router.post("/", response_model=Conversion, status_code=status.HTTP_201_CREATED)
async def create_conversion(
    conversion_in: ConversionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Conversion:
    """
    Create new conversion job.
    
    Args:
        conversion_in: Conversion details
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Created conversion job
        
    Raises:
        HTTPException: If file or conversion type not found
    """
    from app.repositories.repositories import FileRepository
    
    # Verify file belongs to user
    file_repo = FileRepository(db)
    file = await file_repo.get_by_id(conversion_in.file_id)
    
    if not file or file.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )
    
    # Create conversion
    service = ConversionService(db)
    conversion = await service.create_conversion(conversion_in)
    
    await db.commit()
    await db.refresh(conversion)
    
    return conversion


@router.get("/{conversion_id}", response_model=ConversionDetail)
async def get_conversion(
    conversion_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ConversionDetail:
    """
    Get conversion details.
    
    Args:
        conversion_id: Conversion ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Conversion details
        
    Raises:
        HTTPException: If conversion not found or not owned by user
    """
    from app.repositories.repositories import ConversionRepository
    
    repo = ConversionRepository(db)
    conversion = await repo.get_with_details(conversion_id)
    
    if not conversion or conversion.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversion not found",
        )
    
    return conversion


@router.get("/", response_model=PaginatedResponse)
async def list_conversions(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse:
    """
    List user's conversions.
    
    Args:
        skip: Number to skip
        limit: Number to return
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Paginated conversion list
    """
    from app.repositories.repositories import ConversionRepository
    
    repo = ConversionRepository(db)
    conversions = await repo.get_by_user_id(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
    )
    
    # Get total count (simplified)
    total = len(conversions)
    
    return PaginatedResponse(
        items=conversions,
        total=total,
        page=skip // limit + 1,
        page_size=limit,
        total_pages=(total + limit - 1) // limit,
    )


@router.delete("/{conversion_id}")
async def cancel_conversion(
    conversion_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Cancel conversion job (only if not started).
    
    Args:
        conversion_id: Conversion ID
        current_user: Current authenticated user
        db: Database session
        
    Raises:
        HTTPException: If conversion not found, not owned, or already started
    """
    from app.models.models import ConversionStatus
    from app.repositories.repositories import ConversionRepository
    
    repo = ConversionRepository(db)
    conversion = await repo.get_by_id(conversion_id)
    
    if not conversion or conversion.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversion not found",
        )
    
    if conversion.status not in [ConversionStatus.PENDING, ConversionStatus.QUEUED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel conversion that is already processing",
        )
    
    await repo.update(conversion_id, status=ConversionStatus.CANCELLED)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
