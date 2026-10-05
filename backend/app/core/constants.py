"""
Application constants and enumerations.

Defines all constant values and enums used throughout the application.
Ensures consistency and makes changes easier to manage.
"""

from enum import Enum


class UserRole(str, Enum):
    """User role enumeration."""

    SUPERUSER = "superuser"
    ADMIN = "admin"
    PREMIUM = "premium"
    USER = "user"
    GUEST = "guest"


class SubscriptionPlan(str, Enum):
    """Subscription plan types."""

    FREE = "free"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class SubscriptionStatus(str, Enum):
    """Subscription status."""

    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    PENDING_PAYMENT = "pending_payment"
    SUSPENDED = "suspended"


class ConversionStatus(str, Enum):
    """Conversion job status."""

    PENDING = "pending"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ConversionType(str, Enum):
    """Supported conversion types."""

    PDF_TO_DOCX = "pdf_to_docx"
    PDF_TO_EXCEL = "pdf_to_excel"
    PDF_TO_IMAGE = "pdf_to_image"
    JPG_TO_PNG = "jpg_to_png"
    PNG_TO_JPG = "png_to_jpg"
    IMAGE_TO_PDF = "image_to_pdf"
    IMAGES_TO_PDF = "images_to_pdf"
    EXCEL_TO_PDF = "excel_to_pdf"
    OCR = "ocr"
    AI_SUMMARY = "ai_summary"


class FileType(str, Enum):
    """File type enumeration."""

    PDF = "pdf"
    DOCX = "docx"
    XLSX = "xlsx"
    JPG = "jpg"
    PNG = "png"
    TXT = "txt"
    JSON = "json"


class StorageType(str, Enum):
    """Storage type enumeration."""

    LOCAL = "local"
    S3 = "s3"
    TEMP = "temp"


class PaymentStatus(str, Enum):
    """Payment status enumeration."""

    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class NotificationType(str, Enum):
    """Notification type enumeration."""

    CONVERSION_COMPLETE = "conversion_complete"
    CONVERSION_FAILED = "conversion_failed"
    SUBSCRIPTION_EXPIRING = "subscription_expiring"
    PAYMENT_FAILED = "payment_failed"
    SYSTEM_ALERT = "system_alert"
    BATCH_COMPLETE = "batch_complete"


class OCRStatus(str, Enum):
    """OCR processing status."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# ============================================================
# MIME TYPES
# ============================================================

ALLOWED_MIME_TYPES = {
    "pdf": "application/pdf",

    "docx": (
        "application/vnd.openxmlformats-officedocument."
        "wordprocessingml.document"
    ),

    "xlsx": (
        "application/vnd.openxmlformats-officedocument."
        "spreadsheetml.sheet"
    ),

    "jpg": "image/jpeg",
    "png": "image/png",
    "txt": "text/plain",
    "json": "application/json",
}


# ============================================================
# UPLOAD VALIDATION
# ============================================================
#
# These are the file types allowed by the general upload endpoint:
#
# POST /api/v1/files/upload
#
# Keep this list synchronized with the conversion features
# supported by the application.
#

UPLOAD_ALLOWED_MIME_TYPES = {
    "pdf": "application/pdf",

    "docx": (
        "application/vnd.openxmlformats-officedocument."
        "wordprocessingml.document"
    ),

    "xlsx": (
        "application/vnd.openxmlformats-officedocument."
        "spreadsheetml.sheet"
    ),

    "jpg": "image/jpeg",
    "png": "image/png",
}


UPLOAD_ALLOWED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".xlsx",
    ".jpg",
    ".jpeg",
    ".png",
}


# ============================================================
# FILE EXTENSIONS BY TYPE
# ============================================================

FILE_EXTENSIONS = {
    "pdf": [".pdf"],
    "docx": [".docx"],
    "xlsx": [".xlsx"],
    "jpg": [".jpg", ".jpeg"],
    "png": [".png"],
    "txt": [".txt"],
    "json": [".json"],
}


# ============================================================
# STORAGE LIMITS
# ============================================================

FREE_PLAN_MONTHLY_STORAGE_GB = 1
BASIC_PLAN_MONTHLY_STORAGE_GB = 10
PROFESSIONAL_PLAN_MONTHLY_STORAGE_GB = 100
ENTERPRISE_PLAN_MONTHLY_STORAGE_GB = 1000


FREE_PLAN_MONTHLY_CONVERSIONS = 10
BASIC_PLAN_MONTHLY_CONVERSIONS = 100
PROFESSIONAL_PLAN_MONTHLY_CONVERSIONS = 1000
ENTERPRISE_PLAN_MONTHLY_CONVERSIONS = -1  # Unlimited


# ============================================================
# PROCESSING LIMITS
# ============================================================

DEFAULT_MAX_RETRY_ATTEMPTS = 3

DEFAULT_TASK_TIMEOUT = 3600  # 1 hour in seconds

DEFAULT_TASK_SOFT_TIMEOUT = 3000  # 50 minutes in seconds


# ============================================================
# PAGINATION
# ============================================================

DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100


# ============================================================
# CACHE TTL
# ============================================================

CACHE_TTL_SECONDS = 3600  # 1 hour

SHORT_CACHE_TTL = 300  # 5 minutes

LONG_CACHE_TTL = 86400  # 1 day