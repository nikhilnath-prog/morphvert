"""
Service layer for business logic.

Services contain the core business logic, separated from API routes
and database layer. Uses repository pattern for data access.
"""

from datetime import datetime, timedelta
from typing import Optional, List
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.config import settings
from app.core.constants import UserRole
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
    verify_token,
)
from app.models.models import User, Conversion, ConversionStatus, File
from app.repositories.repositories import (
    ConversionRepository,
    RoleRepository,
    SessionRepository,
    UserRepository,
)
from app.schemas.schemas import LoginRequest, TokenResponse, UserCreate, ConversionCreate


def _password_length_http_error(exc: ValueError) -> HTTPException:
    """Translate bcrypt password length errors into a validation-style HTTP error."""
    return HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=str(exc),
    )


class UserService:
    """User management service."""

    def __init__(self, db: AsyncSession):
        self.repository = UserRepository(db)

    async def create_user(self, user_create: UserCreate) -> User:
        """Create new user with hashed password."""
        try:
            hashed_password = hash_password(user_create.password)
        except ValueError as exc:
            raise _password_length_http_error(exc)

        user = await self.repository.create(
            email=user_create.email,
            username=user_create.username,
            hashed_password=hashed_password,
            full_name=user_create.full_name,
        )
        return user

    async def authenticate_user(
        self, email: str, password: str
    ) -> Optional[User]:
        """Authenticate user with email and password."""
        user = await self.repository.get_by_email(email)
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        return user

    async def authenticate_user_by_identifier(
        self,
        identifier: str,
        password: str,
    ) -> Optional[User]:
        """Authenticate user with either email or username and password."""
        user = await self.repository.get_by_email(identifier)
        if not user:
            user = await self.repository.get_by_username(identifier)

        if not user:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        return user

    async def login_user_by_identifier(
        self,
        identifier: str,
        password: str,
        *,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
        device_name: Optional[str] = None,
        device_type: Optional[str] = None,
    ) -> TokenResponse:
        """Authenticate by email or username and create a refresh session."""
        user = await self.authenticate_user_by_identifier(identifier, password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        now = datetime.utcnow()
        if user.locked_until and user.locked_until > now:
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail="Account is temporarily locked. Please try again later.",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive",
            )

        user.login_attempt_count = 0
        user.locked_until = None
        user.last_login_at = now

        token_response = self._build_token_response(user.id)
        await self.session_repository.create_session(
            user_id=user.id,
            token=token_response.refresh_token,
            expires_at=now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            user_agent=user_agent,
            ip_address=ip_address,
            device_name=device_name,
            device_type=device_type,
        )

        await self.db.commit()
        return token_response

    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        return await self.repository.get_by_id(user_id)

    async def update_user(self, user_id: UUID, **kwargs) -> Optional[User]:
        """Update user fields."""
        return await self.repository.update(user_id, **kwargs)

    async def delete_user(self, user_id: UUID) -> bool:
        """Soft delete user."""
        await self.repository.soft_delete(user_id)
        return True


class ConversionService:
    """Conversion job management service."""

    def __init__(self, db: AsyncSession):
        self.repository = ConversionRepository(db)
        self.db = db

    async def create_conversion(
        self, conversion_create: ConversionCreate
    ) -> Conversion:
        """Create new conversion job."""
        conversion = await self.repository.create(
            user_id=conversion_create.user_id,
            file_id=conversion_create.file_id,
            conversion_type_id=conversion_create.conversion_type_id,
            status=ConversionStatus.PENDING,
            conversion_parameters=conversion_create.conversion_parameters,
        )
        return conversion

    async def get_user_conversions(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 20,
    ) -> List[Conversion]:
        """Get user's conversions with pagination."""
        return await self.repository.get_by_user_id(
            user_id=user_id,
            skip=skip,
            limit=limit,
        )

    async def update_conversion_progress(
        self,
        conversion_id: UUID,
        progress_percentage: int,
        **kwargs,
    ) -> Optional[Conversion]:
        """Update conversion progress."""
        return await self.repository.update(
            conversion_id,
            progress_percentage=progress_percentage,
            **kwargs,
        )

    async def mark_conversion_completed(
        self,
        conversion_id: UUID,
        output_file_id: UUID,
        processing_time: int,
    ) -> Optional[Conversion]:
        """Mark conversion as completed."""
        return await self.repository.update(
            conversion_id,
            status=ConversionStatus.COMPLETED,
            output_file_id=output_file_id,
            processing_time_seconds=processing_time,
        )

    async def mark_conversion_failed(
        self,
        conversion_id: UUID,
        error_message: str,
        error_code: str = "CONVERSION_FAILED",
    ) -> Optional[Conversion]:
        """Mark conversion as failed."""
        return await self.repository.update(
            conversion_id,
            status=ConversionStatus.FAILED,
            error_message=error_message,
            error_code=error_code,
        )


class FileService:
    """File management service."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_file_record(
        self,
        user_id: UUID,
        filename: str,
        original_filename: str,
        file_type: str,
        mime_type: str,
        file_size: int,
        storage_path: str,
    ) -> File:
        """Create file metadata record."""
        file = File(
            user_id=user_id,
            filename=filename,
            original_filename=original_filename,
            file_type=file_type,
            mime_type=mime_type,
            file_size=file_size,
            storage_path=storage_path,
        )
        self.db.add(file)
        await self.db.flush()
        return file

    async def get_file_by_id(self, file_id: UUID) -> Optional[File]:
        """Get file by ID."""
        result = await self.db.execute(
            select(File).where(File.id == file_id)
        )
        return result.scalars().first()


class AuthService:
    """Authentication and session management service."""

    DEFAULT_ROLE_NAME = UserRole.USER.value
    DEFAULT_ROLE_DESCRIPTION = "Default Morphvert authenticated user"
    DEFAULT_ROLE_PERMISSIONS = {
        "auth": ["read"],
        "files": ["create", "read", "delete"],
        "conversions": ["create", "read", "cancel"],
    }
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_MINUTES = 15

    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repository = UserRepository(db)
        self.role_repository = RoleRepository(db)
        self.session_repository = SessionRepository(db)

    def _build_token_response(self, user_id: UUID) -> TokenResponse:
        """Create a standard access/refresh token response."""
        return TokenResponse(
            access_token=create_access_token(user_id),
            refresh_token=create_refresh_token(user_id),
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    async def _get_default_role(self):
        """Fetch or create the default role for new users."""
        return await self.role_repository.get_or_create_default_role(
            name=self.DEFAULT_ROLE_NAME,
            description=self.DEFAULT_ROLE_DESCRIPTION,
            permissions=self.DEFAULT_ROLE_PERMISSIONS,
        )

    async def register_user(
        self,
        user_create: UserCreate,
        *,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
        device_name: Optional[str] = None,
        device_type: Optional[str] = None,
    ) -> TokenResponse:
        """Register a new user, issue tokens, and create a session."""
        email = user_create.email.lower().strip()
        username = user_create.username.strip()

        existing_email = await self.user_repository.get_by_email(email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email is already registered",
            )

        existing_username = await self.user_repository.get_by_username(username)
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username is already taken",
            )

        try:
            default_role = await self._get_default_role()
            now = datetime.utcnow()
            try:
                hashed_password = hash_password(user_create.password)
            except ValueError as exc:
                raise _password_length_http_error(exc)

            user = await self.user_repository.create(
                email=email,
                username=username,
                hashed_password=hashed_password,
                full_name=user_create.full_name,
                company=user_create.company,
                role_id=default_role.id,
                is_active=True,
                is_verified=False,
                password_changed_at=now,
                last_login_at=now,
                login_attempt_count=0,
                locked_until=None,
            )

            token_response = self._build_token_response(user.id)
            await self.session_repository.create_session(
                user_id=user.id,
                token=token_response.refresh_token,
                expires_at=now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
                user_agent=user_agent,
                ip_address=ip_address,
                device_name=device_name,
                device_type=device_type,
            )

            await self.db.commit()
            await self.db.refresh(user)
            return token_response
        except IntegrityError:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Unable to create user account",
            )

    async def login_user_by_identifier(
        self,
        identifier: str,
        password: str,
        *,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
        device_name: Optional[str] = None,
        device_type: Optional[str] = None,
    ) -> TokenResponse:
        """Authenticate with either email or username and create a refresh session."""
        user = await self.user_repository.get_by_email(identifier)
        if not user:
            user = await self.user_repository.get_by_username(identifier)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        if not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        now = datetime.utcnow()
        if user.locked_until and user.locked_until > now:
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail="Account is temporarily locked. Please try again later.",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive",
            )

        user.login_attempt_count = 0
        user.locked_until = None
        user.last_login_at = now

        token_response = self._build_token_response(user.id)
        await self.session_repository.create_session(
            user_id=user.id,
            token=token_response.refresh_token,
            expires_at=now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            user_agent=user_agent,
            ip_address=ip_address,
            device_name=device_name,
            device_type=device_type,
        )

        await self.db.commit()
        return token_response

    async def login_user(
        self,
        login_request: LoginRequest,
        *,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
        device_name: Optional[str] = None,
        device_type: Optional[str] = None,
    ) -> TokenResponse:
        """Authenticate a user and create a refresh session."""
        return await self.login_user_by_identifier(
            identifier=login_request.email,
            password=login_request.password,
            user_agent=user_agent,
            ip_address=ip_address,
            device_name=device_name,
            device_type=device_type,
        )

    async def refresh_tokens(self, refresh_token: str) -> TokenResponse:
        """Rotate refresh token and issue a new token pair."""
        payload = verify_token(refresh_token, token_type="refresh")
        user_id = UUID(payload["sub"])
        session = await self.session_repository.get_by_token(refresh_token)

        if not session or not session.is_active or session.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )

        now = datetime.utcnow()
        if session.expires_at and session.expires_at < now:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has expired",
            )

        user = await self.user_repository.get_by_id(user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive",
            )

        token_response = self._build_token_response(user.id)
        await self.session_repository.rotate_refresh_token(
            current_token=refresh_token,
            new_token=token_response.refresh_token,
            new_expires_at=now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )

        await self.db.commit()
        return token_response

    async def logout(self, refresh_token: str, current_user: User) -> None:
        """Revoke the refresh-token session for the current user."""
        session = await self.session_repository.get_by_token(refresh_token)
        if not session or session.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )

        session.is_active = False
        session.last_activity_at = datetime.utcnow()
        await self.db.commit()
