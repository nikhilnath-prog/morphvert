"""
Repository layer for data access.

Repositories handle all database queries, providing a clean
abstraction layer between services and database models.
"""

from datetime import datetime, timedelta
from typing import Optional, List, Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.models.models import Role, Session as AuthSession, User, Conversion, File, ConversionLog
from app.schemas.schemas import UserCreate


class BaseRepository:
    """Base repository with common CRUD operations."""

    def __init__(self, db: AsyncSession, model: Any):
        self.db = db
        self.model = model

    async def get_by_id(self, id: UUID) -> Optional[Any]:
        """Get record by ID."""
        result = await self.db.execute(
            select(self.model).where(
                self.model.id == id,
                self.model.is_deleted == False,
            )
        )
        return result.scalars().first()

    async def get_all(
        self, skip: int = 0, limit: int = 100
    ) -> List[Any]:
        """Get all records with pagination."""
        result = await self.db.execute(
            select(self.model)
            .where(self.model.is_deleted == False)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def create(self, **kwargs) -> Any:
        """Create new record."""
        obj = self.model(**kwargs)
        self.db.add(obj)
        await self.db.flush()
        return obj

    async def update(self, id: UUID, **kwargs) -> Optional[Any]:
        """Update record."""
        obj = await self.get_by_id(id)
        if not obj:
            return None

        for key, value in kwargs.items():
            setattr(obj, key, value)

        await self.db.flush()
        return obj

    async def soft_delete(self, id: UUID) -> bool:
        """Soft delete record."""
        obj = await self.get_by_id(id)
        if not obj:
            return False

        obj.is_deleted = True
        await self.db.flush()
        return True


class UserRepository(BaseRepository):
    """User data access repository."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, User)

    def _base_query(self):
        return select(User).options(selectinload(User.role)).where(User.is_deleted == False)

    async def get_by_id(self, id: UUID) -> Optional[User]:
        """Get user by ID with role eagerly loaded."""
        result = await self.db.execute(
            self._base_query().where(User.id == id)
        )
        return result.scalars().first()

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email with role eagerly loaded."""
        result = await self.db.execute(
            self._base_query().where(User.email == email)
        )
        return result.scalars().first()

    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username with role eagerly loaded."""
        result = await self.db.execute(
            self._base_query().where(User.username == username)
        )
        return result.scalars().first()

    async def email_exists(self, email: str) -> bool:
        """Check if email already exists."""
        result = await self.db.execute(
            self._base_query().where(User.email == email)
        )
        return result.scalars().first() is not None

    async def get_with_role(self, user_id: UUID) -> Optional[User]:
        """Get user with role relationship loaded."""
        return await self.get_by_id(user_id)


class RoleRepository(BaseRepository):
    """Role data access repository."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, Role)

    async def get_by_name(self, name: str) -> Optional[Role]:
        """Get role by name."""
        result = await self.db.execute(
            select(Role).where(
                Role.name == name,
                Role.is_deleted == False,
            )
        )
        return result.scalars().first()

    async def get_or_create_default_role(
        self,
        name: str,
        description: str,
        permissions: dict,
    ) -> Role:
        """Get the default role or create it if missing."""
        role = await self.get_by_name(name)
        if role:
            return role

        role = Role(
            name=name,
            description=description,
            permissions=permissions,
        )
        self.db.add(role)

        try:
            await self.db.flush()
        except IntegrityError:
            await self.db.rollback()
            role = await self.get_by_name(name)
            if role:
                return role
            raise

        return role


class SessionRepository(BaseRepository):
    """Session data access repository."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, AuthSession)

    async def create_session(
        self,
        *,
        user_id: UUID,
        token: str,
        expires_at: datetime,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
        device_name: Optional[str] = None,
        device_type: Optional[str] = None,
    ) -> AuthSession:
        """Create a new refresh-token session."""
        session = AuthSession(
            user_id=user_id,
            token=token,
            expires_at=expires_at,
            user_agent=user_agent,
            ip_address=ip_address,
            device_name=device_name,
            device_type=device_type,
            is_active=True,
            last_activity_at=datetime.utcnow(),
        )
        self.db.add(session)
        await self.db.flush()
        return session

    async def get_by_token(self, token: str) -> Optional[AuthSession]:
        """Get session by stored refresh token."""
        result = await self.db.execute(
            select(AuthSession).where(
                AuthSession.token == token,
                AuthSession.is_deleted == False,
            )
        )
        return result.scalars().first()

    async def deactivate_by_token(self, token: str) -> bool:
        """Deactivate a session by refresh token."""
        session = await self.get_by_token(token)
        if not session:
            return False

        session.is_active = False
        session.last_activity_at = datetime.utcnow()
        await self.db.flush()
        return True

    async def deactivate_by_user_id(self, user_id: UUID) -> int:
        """Deactivate all sessions for a user."""
        result = await self.db.execute(
            select(AuthSession).where(
                AuthSession.user_id == user_id,
                AuthSession.is_deleted == False,
                AuthSession.is_active == True,
            )
        )
        sessions = result.scalars().all()
        for session in sessions:
            session.is_active = False
            session.last_activity_at = datetime.utcnow()
        await self.db.flush()
        return len(sessions)

    async def rotate_refresh_token(
        self,
        current_token: str,
        new_token: str,
        new_expires_at: datetime,
    ) -> Optional[AuthSession]:
        """Rotate a refresh token during token refresh."""
        session = await self.get_by_token(current_token)
        if not session:
            return None

        session.token = new_token
        session.expires_at = new_expires_at
        session.last_activity_at = datetime.utcnow()
        session.is_active = True
        await self.db.flush()
        return session


class ConversionRepository(BaseRepository):
    """Conversion job data access repository."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, Conversion)

    async def get_by_user_id(
        self, user_id: UUID, skip: int = 0, limit: int = 20
    ) -> List[Conversion]:
        """Get user's conversions."""
        result = await self.db.execute(
            select(Conversion)
            .where(
                Conversion.user_id == user_id,
                Conversion.is_deleted == False,
            )
            .order_by(Conversion.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_by_task_id(self, task_id: str) -> Optional[Conversion]:
        """Get conversion by Celery task ID."""
        result = await self.db.execute(
            select(Conversion).where(
                Conversion.task_id == task_id,
                Conversion.is_deleted == False,
            )
        )
        return result.scalars().first()

    async def get_pending_conversions(
        self, limit: int = 100
    ) -> List[Conversion]:
        """Get pending conversions for processing."""
        from app.models.models import ConversionStatus
        
        result = await self.db.execute(
            select(Conversion)
            .where(
                Conversion.status.in_(
                    [ConversionStatus.PENDING, ConversionStatus.QUEUED]
                ),
                Conversion.is_deleted == False,
            )
            .order_by(Conversion.priority.desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def get_with_details(
        self, conversion_id: UUID
    ) -> Optional[Conversion]:
        """Get conversion with all relationships loaded."""
        result = await self.db.execute(
            select(Conversion)
            .where(
                Conversion.id == conversion_id,
                Conversion.is_deleted == False,
            )
            .options(
                selectinload(Conversion.file),
                selectinload(Conversion.conversion_type),
                selectinload(Conversion.logs),
            )
        )
        return result.scalars().first()


class FileRepository(BaseRepository):
    """File metadata data access repository."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, File)

    async def get_by_user_id(
        self, user_id: UUID, skip: int = 0, limit: int = 20
    ) -> List[File]:
        """Get user's files."""
        result = await self.db.execute(
            select(File)
            .where(
                File.user_id == user_id,
                File.is_deleted == False,
            )
            .order_by(File.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_expired_files(self) -> List[File]:
        """Get files that have expired."""
        from sqlalchemy import and_
        from datetime import datetime
        
        result = await self.db.execute(
            select(File).where(
                and_(
                    File.expiry_date <= datetime.utcnow(),
                    File.is_deleted == False,
                )
            )
        )
        return result.scalars().all()
