"""Add configuration columns to data_sources for integration setup.

Revision ID: 008
Revises: 007
Create Date: 2025-01-01 00:00:00.000000

Adds auth_method, auth_config (JSONB), sync_schedule, and sync_enabled
to support per-source integration configuration via the admin UI.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision: str = "008"
down_revision: Union[str, None] = "007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "data_sources",
        sa.Column("auth_method", sa.String(50), nullable=True),
    )
    op.add_column(
        "data_sources",
        # TODO: encrypt at rest in production (use pgcrypto or app-level encryption)
        sa.Column("auth_config", JSONB, nullable=True),
    )
    op.add_column(
        "data_sources",
        sa.Column(
            "sync_schedule",
            sa.String(20),
            nullable=False,
            server_default="manual",
        ),
    )
    op.add_column(
        "data_sources",
        sa.Column(
            "sync_enabled",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )


def downgrade() -> None:
    op.drop_column("data_sources", "sync_enabled")
    op.drop_column("data_sources", "sync_schedule")
    op.drop_column("data_sources", "auth_config")
    op.drop_column("data_sources", "auth_method")
