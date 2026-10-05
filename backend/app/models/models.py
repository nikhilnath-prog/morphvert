"""
SQLAlchemy database models for Morphvert.

Comprehensive model definitions for all entities including:
- User management (users, roles, sessions, api_keys)
- Conversion system (files, conversions, conversion_types, jobs)
- Subscription & payments
- Advanced features (OCR, AI summaries, storage)
- System management (logs, settings)

All models use UUIDs, timestamps, proper indexing, and soft-delete support.
"""

from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text, Enum,
    ForeignKey, Index, UniqueConstraint, CheckConstraint,
    LargeBinary, JSON, DECIMAL
)
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import relationship

from app.models.base import Base, IdMixin, TimestampMixin, SoftDeleteMixin
from app.core.constants import (
    UserRole, SubscriptionPlan, SubscriptionStatus, ConversionStatus,
    ConversionType, FileType, StorageType, PaymentStatus,
    NotificationType, OCRStatus
)


# ===== AUTHENTICATION & USER MANAGEMENT =====

class Role(IdMixin, TimestampMixin, SoftDeleteMixin, Base):
    """User roles for role-based access control (RBAC)."""
    __tablename__ = "roles"

    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text)
    permissions = Column(JSON, default=dict)  # JSON-stored permissions

    # Relationships
    users = relationship("User", back_populates="role")

    __table_args__ = (
        Index("idx_role_name", "name"),
    )


class User(IdMixin, TimestampMixin, SoftDeleteMixin, Base):
    """Main user entity for authentication and profile management."""
    __tablename__ = "users"

    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    
    # Status management
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_verified = Column(Boolean, default=False, nullable=False)
    email_verified_at = Column(DateTime)
    
    # Profile
    avatar_url = Column(String(500))
    bio = Column(Text)
    phone = Column(String(20))
    company = Column(String(255))
    
    # Security
    password_changed_at = Column(DateTime, default=datetime.utcnow)
    last_login_at = Column(DateTime)
    login_attempt_count = Column(Integer, default=0)
    locked_until = Column(DateTime)  # Account lockout time
    
    # Foreign keys
    role_id = Column(PostgresUUID(as_uuid=True), ForeignKey("roles.id"), nullable=False)
    
    # Relationships
    role = relationship("Role", back_populates="users")
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    api_keys = relationship("APIKey", back_populates="user", cascade="all, delete-orphan")
    files = relationship("File", back_populates="user", cascade="all, delete-orphan")
    conversions = relationship("Conversion", back_populates="user", cascade="all, delete-orphan")
    subscription = relationship("Subscription", back_populates="user", uselist=False, cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    storage_usage = relationship("StorageUsage", back_populates="user", uselist=False, cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_user_email", "email"),
        Index("idx_user_username", "username"),
        Index("idx_user_is_active", "is_active"),
        UniqueConstraint("email", name="uq_user_email"),
    )


class Session(IdMixin, TimestampMixin, SoftDeleteMixin, Base):
    """User session management for tracking user activity and device management."""
    __tablename__ = "sessions"

    user_id = Column(PostgresUUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    token = Column(String(500), nullable=False, unique=True, index=True)
    user_agent = Column(String(500))
    ip_address = Column(String(45))  # IPv6 support
    
    # Session lifetime
    expires_at = Column(DateTime, nullable=False, index=True)
    last_activity_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # Device information
    device_name = Column(String(255))
    device_type = Column(String(50))  # mobile, desktop, tablet

    # Relationships
    user = relationship("User", back_populates="sessions")

    __table_args__ = (
        Index("idx_session_user_id", "user_id"),
        Index("idx_session_token", "token"),
        Index("idx_session_expires_at", "expires_at"),
    )


class APIKey(IdMixin, TimestampMixin, SoftDeleteMixin, Base):
    """API keys for programmatic access to the platform."""
    __tablename__ = "api_keys"

    user_id = Column(PostgresUUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    key = Column(String(255), unique=True, nullable=False, index=True)
    key_hash = Column(String(255), nullable=False)  # Hashed for security
    name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Permissions and scopes
    scopes = Column(JSON, default=list)  # List of allowed scopes
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    last_used_at = Column(DateTime)
    expires_at = Column(DateTime)  # Optional expiration
    
    # Tracking
    created_by_ip = Column(String(45))
    used_count = Column(Integer, default=0)

    # Relationships
    user = relationship("User", back_populates="api_keys")

    __table_args__ = (
        Index("idx_api_key_user_id", "user_id"),
        Index("idx_api_key_key", "key"),
        Index("idx_api_key_is_active", "is_active"),
    )


# ===== CONVERSION SYSTEM =====

class ConversionTypeModel(IdMixin, TimestampMixin, SoftDeleteMixin, Base):
    """Supported conversion types and their configurations."""
    __tablename__ = "conversion_types"

    type_name = Column(String(100), unique=True, nullable=False, index=True)
    source_format = Column(String(50), nullable=False)
    target_format = Column(String(50), nullable=False)
    description = Column(Text)
    
    # Configuration
    max_file_size = Column(Integer)  # In bytes
    processing_timeout = Column(Integer, default=3600)  # In seconds
    retry_attempts = Column(Integer, default=3)
    
    # Feature flags
    requires_ocr = Column(Boolean, default=False)
    supports_batch = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # Metadata
    processing_queue = Column(String(100), default="default")
    estimated_processing_time = Column(Integer)  # In seconds

    # Relationships
    conversions = relationship("Conversion", back_populates="conversion_type")

    __table_args__ = (
        Index("idx_conversion_type_name", "type_name"),
        Index("idx_conversion_type_is_active", "is_active"),
    )


class File(IdMixin, TimestampMixin, SoftDeleteMixin, Base):
    """Uploaded files metadata and storage tracking."""
    __tablename__ = "files"

    user_id = Column(PostgresUUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    
    # File information
    filename = Column(String(500), nullable=False)
    original_filename = Column(String(500), nullable=False)
    file_type = Column(Enum(FileType), nullable=False, index=True)
    mime_type = Column(String(100), nullable=False)
    
    # Storage information
    storage_type = Column(Enum(StorageType), default=StorageType.LOCAL, nullable=False)
    storage_path = Column(String(1000), nullable=False)  # Local path or S3 key
    s3_bucket = Column(String(255))  # S3 bucket name if applicable
    s3_key = Column(String(1000))  # S3 key if applicable
    
    # File statistics
    file_size = Column(Integer, nullable=False)  # In bytes
    checksum = Column(String(64))  # SHA256 hash for integrity verification
    
    # Metadata
    is_public = Column(Boolean, default=False, nullable=False)
    is_converted = Column(Boolean, default=False, nullable=False, index=True)
    expiry_date = Column(DateTime)  # For temporary files
    description = Column(Text)
    tags = Column(JSON, default=list)  # Array of tags for organization
    
    # Tracking
    download_count = Column(Integer, default=0)
    virus_scan_status = Column(String(50), default="pending")  # pending, scanned, infected

    # Relationships
    user = relationship("User", back_populates="files")
    conversions = relationship(
        "Conversion",
        back_populates="file",
        foreign_keys="Conversion.file_id",
    )
    conversion_logs = relationship("ConversionLog", back_populates="file")

    __table_args__ = (
        Index("idx_file_user_id", "user_id"),
        Index("idx_file_type", "file_type"),
        Index("idx_file_storage_type", "storage_type"),
        Index("idx_file_is_converted", "is_converted"),
    )


class Conversion(IdMixin, TimestampMixin, SoftDeleteMixin, Base):
    """Conversion jobs for file transformation tracking."""
    __tablename__ = "conversions"

    user_id = Column(PostgresUUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    file_id = Column(PostgresUUID(as_uuid=True), ForeignKey("files.id"), nullable=False, index=True)
    conversion_type_id = Column(PostgresUUID(as_uuid=True), ForeignKey("conversion_types.id"), nullable=False, index=True)
    
    # Status tracking
    status = Column(Enum(ConversionStatus), default=ConversionStatus.PENDING, nullable=False, index=True)
    progress_percentage = Column(Integer, default=0, nullable=False)
    
    # Processing
    task_id = Column(String(255), unique=True)  # Celery task ID
    worker_id = Column(String(255))  # Celery worker ID
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    processing_time_seconds = Column(Integer)  # Total processing time
    
    # Output
    output_file_id = Column(PostgresUUID(as_uuid=True), ForeignKey("files.id"))
    output_filename = Column(String(500))
    
    # Error handling
    error_message = Column(Text)
    error_code = Column(String(50))
    retry_count = Column(Integer, default=0)
    next_retry_at = Column(DateTime)
    
    # Configuration
    conversion_parameters = Column(JSON, default=dict)  # Additional parameters
    priority = Column(Integer, default=0)  # For queue prioritization

    # Relationships
    user = relationship("User", back_populates="conversions")
    file = relationship("File", back_populates="conversions", foreign_keys=[file_id])
    output_file = relationship("File", foreign_keys=[output_file_id])
    conversion_type = relationship("ConversionTypeModel", back_populates="conversions")
    logs = relationship("ConversionLog", back_populates="conversion", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_conversion_user_id", "user_id"),
        Index("idx_conversion_file_id", "file_id"),
        Index("idx_conversion_status", "status"),
        Index("idx_conversion_task_id", "task_id"),
        Index("idx_conversion_created_at", "created_at"),
    )


class ConversionLog(IdMixin, TimestampMixin, SoftDeleteMixin, Base):
    """Detailed logs for conversion processing for debugging and auditing."""
    __tablename__ = "conversion_logs"

    conversion_id = Column(PostgresUUID(as_uuid=True), ForeignKey("conversions.id"), nullable=False, index=True)
    file_id = Column(PostgresUUID(as_uuid=True), ForeignKey("files.id"), nullable=False, index=True)
    
    # Log details
    log_level = Column(String(20), nullable=False)  # DEBUG, INFO, WARNING, ERROR
    message = Column(Text, nullable=False)
    details = Column(JSON)  # Additional context
    
    # Source
    source = Column(String(100), nullable=False)  # converter, worker, api

    # Relationships
    conversion = relationship("Conversion", back_populates="logs")
    file = relationship("File", back_populates="conversion_logs")

    __table_args__ = (
        Index("idx_conversion_log_conversion_id", "conversion_id"),
        Index("idx_conversion_log_level", "log_level"),
        Index("idx_conversion_log_created_at", "created_at"),
    )


class Job(IdMixin, TimestampMixin, SoftDeleteMixin, Base):
    """Batch processing jobs for handling multiple conversions."""
    __tablename__ = "jobs"

    user_id = Column(PostgresUUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Job metadata
    name = Column(String(255), nullable=False)
    description = Column(Text)
    job_type = Column(String(50), nullable=False)  # batch_conversion, scheduled_task
    
    # Status
    status = Column(String(50), default="pending", nullable=False, index=True)
    total_items = Column(Integer, nullable=False)
    completed_items = Column(Integer, default=0)
    failed_items = Column(Integer, default=0)
    progress_percentage = Column(Integer, default=0, nullable=False)
    
    # Processing
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    estimated_completion_at = Column(DateTime)
    
    # Configuration
    parameters = Column(JSON, default=dict)
    priority = Column(Integer, default=0)

    __table_args__ = (
        Index("idx_job_user_id", "user_id"),
        Index("idx_job_status", "status"),
        Index("idx_job_created_at", "created_at"),
    )


# ===== SUBSCRIPTION & PAYMENTS =====

class Plan(IdMixin, TimestampMixin, SoftDeleteMixin, Base):
    """Subscription plans offered by the platform."""
    __tablename__ = "plans"

    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    plan_type = Column(Enum(SubscriptionPlan), unique=True, nullable=False, index=True)
    
    # Pricing
    monthly_price = Column(DECIMAL(10, 2), nullable=False)
    annual_price = Column(DECIMAL(10, 2))
    currency = Column(String(3), default="USD")
    
    # Limits
    monthly_storage_gb = Column(Integer, nullable=False)
    monthly_conversions = Column(Integer)  # NULL = unlimited
    max_file_size_mb = Column(Integer, nullable=False)
    max_batch_size = Column(Integer, nullable=False)
    
    # Features
    features = Column(JSON, default=dict)  # Feature flags
    api_access = Column(Boolean, default=False)
    ocr_enabled = Column(Boolean, default=False)
    ai_summary_enabled = Column(Boolean, default=False)
    batch_processing_enabled = Column(Boolean, default=False)
    priority_support = Column(Boolean, default=False)
    
    # Management
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    display_order = Column(Integer, default=0)

    # Relationships
    subscriptions = relationship("Subscription", back_populates="plan")

    __table_args__ = (
        Index("idx_plan_name", "name"),
        Index("idx_plan_type", "plan_type"),
    )


class Subscription(IdMixin, TimestampMixin, SoftDeleteMixin, Base):
    """User subscriptions for plan management."""
    __tablename__ = "subscriptions"

    user_id = Column(PostgresUUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True, unique=True)
    plan_id = Column(PostgresUUID(as_uuid=True), ForeignKey("plans.id"), nullable=False, index=True)
    
    # Status
    status = Column(Enum(SubscriptionStatus), default=SubscriptionStatus.ACTIVE, nullable=False, index=True)
    
    # Billing
    current_period_start = Column(DateTime, nullable=False, default=datetime.utcnow)
    current_period_end = Column(DateTime, nullable=False)
    trial_end = Column(DateTime)  # Trial period expiration
    
    # Usage tracking
    usage_storage_gb = Column(Float, default=0)
    usage_conversions = Column(Integer, default=0)
    
    # Cancellation
    cancellation_reason = Column(Text)
    cancelled_at = Column(DateTime)
    
    # Payment method
    stripe_subscription_id = Column(String(255), unique=True)
    auto_renew = Column(Boolean, default=True)

    # Relationships
    user = relationship("User", back_populates="subscription")
    plan = relationship("Plan", back_populates="subscriptions")
    payments = relationship("Payment", back_populates="subscription", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_subscription_user_id", "user_id"),
        Index("idx_subscription_status", "status"),
        Index("idx_subscription_current_period_end", "current_period_end"),
    )


class Payment(IdMixin, TimestampMixin, SoftDeleteMixin, Base):
    """Payment records for subscription billing."""
    __tablename__ = "payments"

    subscription_id = Column(PostgresUUID(as_uuid=True), ForeignKey("subscriptions.id"), nullable=False, index=True)
    
    # Payment details
    amount = Column(DECIMAL(10, 2), nullable=False)
    currency = Column(String(3), default="USD")
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False, index=True)
    
    # Payment method
    payment_method = Column(String(50), nullable=False)  # stripe, paypal, etc.
    transaction_id = Column(String(255), unique=True, index=True)
    receipt_url = Column(String(500))
    
    # Billing period
    billing_period_start = Column(DateTime, nullable=False)
    billing_period_end = Column(DateTime, nullable=False)
    
    # Error handling
    failure_reason = Column(Text)
    next_retry_at = Column(DateTime)
    retry_count = Column(Integer, default=0)

    # Relationships
    subscription = relationship("Subscription", back_populates="payments")

    __table_args__ = (
        Index("idx_payment_subscription_id", "subscription_id"),
        Index("idx_payment_status", "status"),
        Index("idx_payment_created_at", "created_at"),
    )


# ===== ADVANCED FEATURES =====

class OCRResult(IdMixin, TimestampMixin, SoftDeleteMixin, Base):
    """OCR processing results and extracted text."""
    __tablename__ = "ocr_results"

    file_id = Column(PostgresUUID(as_uuid=True), ForeignKey("files.id"), nullable=False, index=True)
    
    # Processing
    status = Column(Enum(OCRStatus), default=OCRStatus.PENDING, nullable=False, index=True)
    language_detected = Column(String(50))
    confidence_score = Column(Float)  # 0-1 confidence
    
    # Results
    extracted_text = Column(Text)
    raw_text = Column(LargeBinary)  # Raw extraction data
    ocr_metadata = Column(JSON, default=dict)
    
    # Processing details
    processing_time_seconds = Column(Integer)
    worker_id = Column(String(255))
    error_message = Column(Text)

    # Relationships
    file = relationship("File")

    __table_args__ = (
        Index("idx_ocr_file_id", "file_id"),
        Index("idx_ocr_status", "status"),
    )


class AISummary(IdMixin, TimestampMixin, SoftDeleteMixin, Base):
    """AI-generated summaries of document content."""
    __tablename__ = "ai_summaries"

    file_id = Column(PostgresUUID(as_uuid=True), ForeignKey("files.id"), nullable=False, index=True)
    
    # Summary content
    summary = Column(Text, nullable=False)
    bullet_points = Column(JSON, default=list)  # Array of key points
    key_phrases = Column(JSON, default=list)  # Important terms
    
    # Configuration
    summary_length = Column(String(50))  # short, medium, long
    model_used = Column(String(100))  # GPT-4, Claude, etc.
    
    # Quality metrics
    relevance_score = Column(Float)  # 0-1
    readability_score = Column(Float)  # 0-1
    
    # Processing
    processing_time_seconds = Column(Integer)

    # Relationships
    file = relationship("File")

    __table_args__ = (
        Index("idx_ai_summary_file_id", "file_id"),
    )


class StorageUsage(IdMixin, TimestampMixin, SoftDeleteMixin, Base):
    """User storage usage tracking for quota management."""
    __tablename__ = "storage_usage"

    user_id = Column(PostgresUUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True, unique=True)
    
    # Current usage
    total_storage_bytes = Column(Integer, default=0)
    uploaded_files_bytes = Column(Integer, default=0)
    converted_files_bytes = Column(Integer, default=0)
    
    # Quota
    quota_bytes = Column(Integer, nullable=False)
    
    # Tracking
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    files_count = Column(Integer, default=0)
    
    # Monthly reset
    monthly_reset_date = Column(DateTime)

    # Relationships
    user = relationship("User", back_populates="storage_usage")

    __table_args__ = (
        Index("idx_storage_usage_user_id", "user_id"),
    )


# ===== NOTIFICATIONS & SYSTEM =====

class Notification(IdMixin, TimestampMixin, SoftDeleteMixin, Base):
    """User notifications for system events and alerts."""
    __tablename__ = "notifications"

    user_id = Column(PostgresUUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Notification details
    notification_type = Column(Enum(NotificationType), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    data = Column(JSON, default=dict)  # Additional context
    
    # Status
    is_read = Column(Boolean, default=False, nullable=False, index=True)
    read_at = Column(DateTime)
    
    # Delivery
    sent_via_email = Column(Boolean, default=False)
    sent_via_push = Column(Boolean, default=False)
    action_url = Column(String(500))  # Link to take action

    # Relationships
    user = relationship("User", back_populates="notifications")

    __table_args__ = (
        Index("idx_notification_user_id", "user_id"),
        Index("idx_notification_type", "notification_type"),
        Index("idx_notification_is_read", "is_read"),
    )


class SystemSettings(IdMixin, TimestampMixin, SoftDeleteMixin, Base):
    """System-wide settings and configuration."""
    __tablename__ = "system_settings"

    key = Column(String(255), unique=True, nullable=False, index=True)
    value = Column(Text, nullable=False)
    description = Column(Text)
    setting_type = Column(String(50))  # string, integer, boolean, json
    is_mutable = Column(Boolean, default=True)  # Can be changed via API

    __table_args__ = (
        Index("idx_system_settings_key", "key"),
    )


class AdminLog(IdMixin, TimestampMixin, SoftDeleteMixin, Base):
    """Administrative actions audit log for compliance."""
    __tablename__ = "admin_logs"

    admin_id = Column(PostgresUUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Action details
    action = Column(String(100), nullable=False)
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(PostgresUUID(as_uuid=True))
    
    # Details
    changes = Column(JSON, default=dict)  # Before/after values
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    
    # Status
    status = Column(String(50), default="success")  # success, failed

    __table_args__ = (
        Index("idx_admin_log_admin_id", "admin_id"),
        Index("idx_admin_log_action", "action"),
        Index("idx_admin_log_created_at", "created_at"),
    )
