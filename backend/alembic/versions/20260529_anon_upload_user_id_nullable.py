"""Make files.user_id nullable for anonymous uploads.

Revision ID: 20260529_anon_upload_user_id_nullable
Revises: 
Create Date: 2026-05-29 23:05:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260529_anon_upload_user_id_nullable"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "files",
        "user_id",
        existing_type=sa.dialects.postgresql.UUID(as_uuid=True),
        nullable=True,
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            "UPDATE files SET user_id = (SELECT id FROM users LIMIT 1) WHERE user_id IS NULL"
        )
    )
    op.alter_column(
        "files",
        "user_id",
        existing_type=sa.dialects.postgresql.UUID(as_uuid=True),
        nullable=False,
    )