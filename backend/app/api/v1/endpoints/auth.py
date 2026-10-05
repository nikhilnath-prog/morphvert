"""Authentication API endpoints for Morphvert."""

from fastapi import APIRouter, Depends, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database.connection import get_db
from app.models.models import User
from app.schemas.schemas import (
    LoginRequest,
    RefreshTokenRequest,
    TokenResponse,
    User as UserSchema,
    UserCreate,
)
from app.services.services import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


def _request_metadata(request: Request) -> dict:
    """Extract session metadata from the incoming HTTP request."""
    client_host = request.client.host if request.client else None
    return {
        "user_agent": request.headers.get("user-agent"),
        "ip_address": client_host,
        "device_name": request.headers.get("x-device-name"),
        "device_type": request.headers.get("x-device-type"),
    }


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Create a new user account and return fresh tokens."""
    service = AuthService(db)
    metadata = _request_metadata(request)
    return await service.register_user(user_in, **metadata)


@router.post("/login", response_model=TokenResponse)
async def login(
    login_in: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Authenticate an existing user and issue tokens."""
    service = AuthService(db)
    metadata = _request_metadata(request)
    return await service.login_user(login_in, **metadata)


@router.post("/token", response_model=TokenResponse)
async def token_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """OAuth2 password-flow login for Swagger UI authorize support."""
    service = AuthService(db)
    metadata = _request_metadata(request) if request else {}
    return await service.login_user_by_identifier(
        identifier=form_data.username,
        password=form_data.password,
        user_agent=metadata.get("user_agent"),
        ip_address=metadata.get("ip_address"),
        device_name=metadata.get("device_name"),
        device_type=metadata.get("device_type"),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_in: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Rotate a refresh token and return a new token pair."""
    service = AuthService(db)
    return await service.refresh_tokens(refresh_in.refresh_token)


@router.post("/logout")
async def logout(
    refresh_in: RefreshTokenRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """Revoke the current refresh-token session."""
    service = AuthService(db)
    await service.logout(refresh_in.refresh_token, current_user)
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserSchema)
async def current_user(current_user: User = Depends(get_current_user)) -> User:
    """Return the authenticated user profile."""
    return current_user
