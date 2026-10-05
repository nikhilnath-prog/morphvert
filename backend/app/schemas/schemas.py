"""
Pydantic schemas for request/response validation and documentation.

Organized by feature domain for better maintainability.
Uses Pydantic v2 with proper validation and documentation.
"""

from typing import List, Optional, Any
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, EmailStr, validator, field_validator


# ===== USER SCHEMAS =====

class RoleBase(BaseModel):
    """Base role schema."""
    name: str = Field(..., min_length=3, max_length=50)
    description: Optional[str] = None
    permissions: dict = Field(default_factory=dict)


class RoleCreate(RoleBase):
    """Schema for creating a role."""
    pass


class RoleUpdate(BaseModel):
    """Schema for updating a role."""
    name: Optional[str] = Field(None, min_length=3, max_length=50)
    description: Optional[str] = None
    permissions: Optional[dict] = None


class Role(RoleBase):
    """Role response schema."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    is_deleted: bool

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    full_name: Optional[str] = Field(None, max_length=255)
    company: Optional[str] = Field(None, max_length=255)


class UserCreate(UserBase):
    """Schema for user registration."""
    password: str = Field(..., min_length=8, max_length=255)
    
    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password has uppercase, lowercase, digit, and special char."""
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain digit")
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in v):
            raise ValueError("Password must contain special character")
        return v


class UserUpdate(BaseModel):
    """Schema for user profile updates."""
    full_name: Optional[str] = Field(None, max_length=255)
    company: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    bio: Optional[str] = None
    avatar_url: Optional[str] = Field(None, max_length=500)


class UserPasswordChange(BaseModel):
    """Schema for password change."""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=255)
    confirm_password: str

    @field_validator("new_password")
    @classmethod
    def validate_new_password_length(cls, v: str) -> str:
        """Keep changed passwords compatible with bcrypt."""
        return v


class User(UserBase):
    """User response schema."""
    id: UUID
    is_active: bool
    is_verified: bool
    last_login_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    role: Role

    class Config:
        from_attributes = True


class UserWithStats(User):
    """User response with usage statistics."""
    total_conversions: int = 0
    total_files: int = 0
    total_storage_gb: float = 0


# ===== AUTHENTICATION SCHEMAS =====

class TokenData(BaseModel):
    """Token payload data."""
    sub: str  # user_id
    exp: datetime
    iat: datetime
    aud: str = "morphvert-api"


class TokenResponse(BaseModel):
    """JWT token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class LoginRequest(BaseModel):
    """User login credentials."""
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    """Refresh token request."""
    refresh_token: str


# ===== SESSION SCHEMAS =====

class SessionCreate(BaseModel):
    """Schema for creating session."""
    device_name: Optional[str] = None
    device_type: Optional[str] = None


class Session(BaseModel):
    """Session response schema."""
    id: UUID
    user_id: UUID
    user_agent: Optional[str]
    ip_address: str
    device_name: Optional[str]
    device_type: Optional[str]
    is_active: bool
    expires_at: datetime
    last_activity_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# ===== API KEY SCHEMAS =====

class APIKeyCreate(BaseModel):
    """Schema for creating API key."""
    name: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = None
    scopes: List[str] = Field(default_factory=lambda: ["read:conversions"])
    expires_at: Optional[datetime] = None


class APIKey(BaseModel):
    """API key response (masked)."""
    id: UUID
    name: str
    description: Optional[str]
    scopes: List[str]
    is_active: bool
    last_used_at: Optional[datetime]
    expires_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class APIKeyWithSecret(APIKey):
    """API key response with secret (only shown once)."""
    key: str


# ===== FILE SCHEMAS =====

class FileBase(BaseModel):
    """Base file schema."""
    filename: str = Field(..., max_length=500)
    description: Optional[str] = None
    tags: List[str] = Field(default_factory=list, max_items=10)


class FileCreate(FileBase):
    """Schema for file creation (upload)."""
    pass


class File(FileBase):
    """File response schema."""
    id: UUID
    user_id: Optional[UUID] = None
    file_type: str
    mime_type: str
    file_size: int
    is_public: bool
    is_converted: bool
    download_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FileWithConversions(File):
    """File response with conversion history."""
    conversions: List["Conversion"] = []


# ===== CONVERSION SCHEMAS =====

class ConversionTypeBase(BaseModel):
    """Base conversion type schema."""
    type_name: str = Field(..., max_length=100)
    source_format: str = Field(..., max_length=50)
    target_format: str = Field(..., max_length=50)


class ConversionType(ConversionTypeBase):
    """Conversion type response."""
    id: UUID
    description: Optional[str]
    max_file_size: Optional[int]
    supports_batch: bool
    requires_ocr: bool
    is_active: bool
    processing_queue: str

    class Config:
        from_attributes = True


class ConversionCreate(BaseModel):
    """Schema for creating conversion job."""
    file_id: UUID
    conversion_type_id: UUID
    conversion_parameters: dict = Field(default_factory=dict)
    priority: int = Field(default=0, ge=0, le=10)


class ConversionUpdate(BaseModel):
    """Schema for updating conversion."""
    conversion_parameters: Optional[dict] = None
    priority: Optional[int] = Field(None, ge=0, le=10)


class Conversion(BaseModel):
    """Conversion response schema."""
    id: UUID
    user_id: UUID
    file_id: UUID
    status: str
    progress_percentage: int
    output_filename: Optional[str]
    processing_time_seconds: Optional[int]
    error_message: Optional[str]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class ConversionDetail(Conversion):
    """Detailed conversion response with more info."""
    conversion_type: ConversionType
    file: File
    output_file: Optional[File] = None


# ===== SUBSCRIPTION SCHEMAS =====

class PlanBase(BaseModel):
    """Base plan schema."""
    name: str = Field(..., max_length=100)
    monthly_price: float = Field(..., ge=0)
    monthly_storage_gb: int = Field(..., ge=0)


class Plan(PlanBase):
    """Plan response schema."""
    id: UUID
    description: Optional[str]
    plan_type: str
    annual_price: Optional[float]
    currency: str
    features: dict
    api_access: bool
    ocr_enabled: bool
    is_active: bool

    class Config:
        from_attributes = True


class SubscriptionBase(BaseModel):
    """Base subscription schema."""
    plan_id: UUID


class SubscriptionCreate(SubscriptionBase):
    """Schema for creating subscription."""
    pass


class Subscription(BaseModel):
    """Subscription response schema."""
    id: UUID
    user_id: UUID
    plan_id: UUID
    status: str
    current_period_start: datetime
    current_period_end: datetime
    usage_storage_gb: float
    usage_conversions: int
    auto_renew: bool
    created_at: datetime

    class Config:
        from_attributes = True


class SubscriptionDetail(Subscription):
    """Detailed subscription response."""
    plan: Plan


# ===== OCR SCHEMAS =====

class OCRResultResponse(BaseModel):
    """OCR result response."""
    id: UUID
    file_id: UUID
    status: str
    language_detected: Optional[str]
    confidence_score: Optional[float]
    extracted_text: Optional[str]
    processing_time_seconds: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


# ===== AI SUMMARY SCHEMAS =====

class AISummaryResponse(BaseModel):
    """AI summary response."""
    id: UUID
    file_id: UUID
    summary: str
    bullet_points: List[str]
    key_phrases: List[str]
    summary_length: str
    relevance_score: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True


# ===== NOTIFICATION SCHEMAS =====

class NotificationCreate(BaseModel):
    """Schema for creating notification."""
    title: str = Field(..., max_length=255)
    message: str
    notification_type: str
    data: dict = Field(default_factory=dict)


class Notification(BaseModel):
    """Notification response."""
    id: UUID
    user_id: UUID
    title: str
    message: str
    notification_type: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ===== PAGINATION SCHEMAS =====

class PaginationParams(BaseModel):
    """Pagination parameters."""
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    sort_by: Optional[str] = None
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")


class PaginatedResponse(BaseModel):
    """Generic paginated response."""
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int


# ===== ERROR SCHEMAS =====

class ErrorResponse(BaseModel):
    """Standard error response."""
    status_code: int
    message: str
    detail: Optional[str] = None
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
