import base64
import os
import sys
from pathlib import Path

import pytest


os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("REDIS_CELERY_URL", "redis://localhost:6379/1")
os.environ.setdefault("CELERY_BROKER_URL", "redis://localhost:6379/1")
os.environ.setdefault("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-morphvert")
os.environ.setdefault("DATABASE_ECHO", "False")
os.environ.setdefault("LOG_LEVEL", "INFO")
os.environ.setdefault("LOCAL_STORAGE_PATH", "./uploads-test")
os.environ.setdefault("CONVERTED_FILES_PATH", "./converted-test")
os.environ.setdefault("TEMP_FILES_PATH", "./temp-test")
os.environ.setdefault("LOGS_DIR", "./logs-test")

BACKEND_ROOT = Path(__file__).resolve().parents[2]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.core.config import settings
from app.services.upload_service import UploadService
from app.utils.file_utils import generate_uuid_filename, validate_file_upload


class DummyUploadFile:
    def __init__(self, filename: str, content_type: str, content: bytes):
        self.filename = filename
        self.content_type = content_type
        self._content = content

    async def read(self) -> bytes:
        return self._content


class FakeDB:
    def __init__(self) -> None:
        self.added = None
        self.committed = False
        self.rolled_back = False

    def add(self, obj):
        self.added = obj

    async def flush(self):
        return None

    async def commit(self):
        self.committed = True

    async def rollback(self):
        self.rolled_back = True


@pytest.mark.asyncio
async def test_upload_service_stores_anonymous_image(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "LOCAL_STORAGE_PATH", str(tmp_path / "uploads"))
    monkeypatch.setattr(settings, "CONVERTED_FILES_PATH", str(tmp_path / "converted"))
    monkeypatch.setattr(settings, "TEMP_FILES_PATH", str(tmp_path / "temp"))
    monkeypatch.setattr(settings, "LOGS_DIR", str(tmp_path / "logs"))
    monkeypatch.setattr(settings, "MAX_FILE_SIZE", 1024 * 1024)

    png_bytes = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO9Y1X8AAAAASUVORK5CYII="
    )
    upload_file = DummyUploadFile("sample.png", "image/png", png_bytes)
    fake_db = FakeDB()

    service = UploadService(fake_db)
    file_record = await service.upload_file(upload_file)

    assert fake_db.committed is True
    assert file_record.user_id is None
    assert file_record.original_filename == "sample.png"
    assert file_record.mime_type == "image/png"
    assert file_record.file_size == len(png_bytes)
    assert file_record.filename.endswith(".png")
    assert (tmp_path / "uploads" / file_record.filename).exists()


def test_validate_file_upload_rejects_unsupported_type():
    is_valid, error_message = validate_file_upload(
        filename="payload.exe",
        mime_type="application/octet-stream",
        file_size=128,
    )

    assert is_valid is False
    assert error_message


def test_generate_uuid_filename_preserves_extension():
    generated = generate_uuid_filename("report.pdf")

    assert generated.endswith(".pdf")
    assert len(generated) > len(".pdf")


def test_excel_validation_rejects_empty_or_wrong_type():
    from app.converters.pdf_tools import ensure_excel_bytes

    empty = b""
    try:
        ensure_excel_bytes("report.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", empty)
        assert False, "Expected validation to reject empty Excel bytes"
    except Exception:
        pass

    try:
        ensure_excel_bytes("report.pdf", "application/pdf", b"not-an-excel")
        assert False, "Expected validation to reject non-XLSX content"
    except Exception:
        pass