"""
Base model configuration for all SQLAlchemy models.

Provides common functionality for all models including timestamps,
UUID primary keys, and soft delete support.
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, declared_attr, declarative_mixin
from sqlalchemy.ext.declarative import DeclarativeMeta


@declarative_mixin
class TimestampMixin:
    """Mixin providing timestamp columns for all models."""
    
    @declared_attr
    def created_at(cls):
        """Timestamp when record was created."""
        return Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    @declared_attr
    def updated_at(cls):
        """Timestamp when record was last updated."""
        return Column(
            DateTime,
            default=datetime.utcnow,
            onupdate=datetime.utcnow,
            nullable=False,
            index=True,
        )


@declarative_mixin
class SoftDeleteMixin:
    """Mixin providing soft delete functionality."""
    
    @declared_attr
    def is_deleted(cls):
        """Soft delete flag for logical deletion."""
        return Column(Boolean, default=False, nullable=False, index=True)


@declarative_mixin
class IdMixin:
    """Mixin providing UUID primary key."""
    
    @declared_attr
    def id(cls):
        """UUID primary key for all entities."""
        return Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)


class CustomBase:
    """Custom base class for all models with common functionality."""
    
    # Allow unmapped attributes for SQLAlchemy 2.0 compatibility
    __allow_unmapped__ = True
    
    def __repr__(self) -> str:
        """String representation of model."""
        return f"<{self.__class__.__name__}(id={self.id if hasattr(self, 'id') else 'N/A'})>"


Base: DeclarativeMeta = declarative_base(cls=CustomBase)
