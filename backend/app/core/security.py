"""
Security utilities for authentication, authorization, and encryption.

Includes JWT token handling, password hashing, and permission checks.
"""

import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from uuid import UUID, uuid4

import bcrypt
from jose import JWTError, jwt
from fastapi import HTTPException, status

from app.core.config import settings

ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"


def _normalize_password(password: str) -> bytes:
    """Normalize any password to a fixed-length digest before bcrypt hashing."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest().encode("utf-8")


def hash_password(password: str) -> str:
    """
    Hash password using bcrypt.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
    """
    normalized_password = _normalize_password(password)
    hashed_password = bcrypt.hashpw(normalized_password, bcrypt.gensalt(rounds=12))
    return hashed_password.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify plain password against hash.
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password
        
    Returns:
        True if password matches, False otherwise
    """
    try:
        normalized_password = _normalize_password(plain_password)
        return bcrypt.checkpw(normalized_password, hashed_password.encode("utf-8"))
    except Exception:
        return False


def create_token(
    subject: UUID,
    token_type: str,
    expires_delta: timedelta,
    additional_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """Create a signed JWT with standard Morphvert claims."""
    now = datetime.now(timezone.utc)
    payload: Dict[str, Any] = {
        "sub": str(subject),
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
        "aud": settings.JWT_AUDIENCE,
        "type": token_type,
        "jti": str(uuid4()),
    }

    if additional_claims:
        payload.update(additional_claims)

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


def create_access_token(
    subject: UUID,
    expires_delta: Optional[timedelta] = None,
    additional_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Create JWT access token.
    
    Args:
        subject: User ID to encode in token
        expires_delta: Custom expiration time (default: settings value)
        additional_claims: Additional claims to include in token
        
    Returns:
        Encoded JWT token
        
    Example:
        token = create_access_token(user_id)
    """
    if expires_delta is None:
        expires_delta = timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    return create_token(
        subject=subject,
        token_type=ACCESS_TOKEN_TYPE,
        expires_delta=expires_delta,
        additional_claims=additional_claims,
    )


def create_refresh_token(subject: UUID) -> str:
    """
    Create JWT refresh token with longer expiration.
    
    Args:
        subject: User ID
        
    Returns:
        Encoded refresh token
    """
    expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    return create_token(
        subject=subject,
        token_type=REFRESH_TOKEN_TYPE,
        expires_delta=expires_delta,
    )


def decode_token(token: str, expected_token_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Verify and decode JWT token.
    
    Args:
        token: JWT token to verify
        expected_token_type: Optional token type to enforce (access or refresh)
        
    Returns:
        Decoded token payload
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            audience=settings.JWT_AUDIENCE,
        )

        if expected_token_type and payload.get("type") != expected_token_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def verify_token(token: str, token_type: Optional[str] = None) -> Dict[str, Any]:
    """Backward-compatible alias for decoding JWT tokens."""
    return decode_token(token=token, expected_token_type=token_type)


def get_user_id_from_token(token: str) -> UUID:
    """
    Extract user ID from token.
    
    Args:
        token: JWT token
        
    Returns:
        User UUID
        
    Raises:
        HTTPException: If token is invalid
    """
    payload = verify_token(token, token_type=ACCESS_TOKEN_TYPE)
    user_id = payload.get("sub")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing user ID",
        )
    
    return UUID(user_id)


def hash_api_key(api_key: str) -> str:
    """Hash API key for secure storage."""
    return hash_password(api_key)


def verify_api_key(plain_key: str, hashed_key: str) -> bool:
    """Verify API key against hash."""
    return verify_password(plain_key, hashed_key)
