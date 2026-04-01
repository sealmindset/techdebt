"""Domain schema -- applications, recommendations, decisions, data_sources, submissions

Revision ID: 004
Revises: 003
Create Date: 2025-01-01 00:00:00.000000

Domain tables for the SaaS rationalization tool (TechDebt).
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- applications ---
    op.create_table(
        "applications",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(255), unique=True, nullable=False),
        sa.Column("vendor", sa.String(255), nullable=False),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("app_type", sa.String(50), nullable=False, server_default=sa.text("'saas'")),
        sa.Column("status", sa.String(50), nullable=False, server_default=sa.text("'active'")),
        sa.Column("annual_cost", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("cost_per_license", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("total_licenses", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("active_users", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("adoption_rate", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("last_login_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("contract_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("contract_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("department", sa.String(100), nullable=False),
        sa.Column("data_source", sa.String(100), nullable=False, server_default=sa.text("'manual'")),
        sa.Column("risk_score", sa.Float(), nullable=True),
        sa.Column("compliance_status", sa.String(50), nullable=True),
        sa.Column("owner_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- recommendations ---
    op.create_table(
        "recommendations",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("application_id", UUID(as_uuid=True), sa.ForeignKey("applications.id", ondelete="CASCADE"), nullable=False),
        sa.Column("recommendation_type", sa.String(50), nullable=False),
        sa.Column("confidence_score", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("reasoning", sa.Text(), nullable=True),
        sa.Column("cost_savings_estimate", sa.Float(), nullable=True),
        sa.Column("alternative_app", sa.String(255), nullable=True),
        sa.Column("evidence", sa.Text(), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default=sa.text("'pending'")),
        sa.Column("created_by", sa.String(100), nullable=False, server_default=sa.text("'ai_engine'")),
        sa.Column("reviewed_by", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- decisions ---
    op.create_table(
        "decisions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("application_id", UUID(as_uuid=True), sa.ForeignKey("applications.id", ondelete="CASCADE"), nullable=False),
        sa.Column("recommendation_id", UUID(as_uuid=True), sa.ForeignKey("recommendations.id"), nullable=True),
        sa.Column("decision_type", sa.String(50), nullable=False),
        sa.Column("justification", sa.Text(), nullable=False),
        sa.Column("submitted_by", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default=sa.text("'pending_review'")),
        sa.Column("reviewer_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("review_notes", sa.Text(), nullable=True),
        sa.Column("target_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cost_impact", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- data_sources ---
    op.create_table(
        "data_sources",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(100), unique=True, nullable=False),
        sa.Column("source_type", sa.String(50), nullable=False),
        sa.Column("base_url", sa.String(500), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default=sa.text("'disconnected'")),
        sa.Column("last_sync_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("records_synced", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- submissions ---
    op.create_table(
        "submissions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("app_name", sa.String(255), nullable=False),
        sa.Column("vendor", sa.String(255), nullable=True),
        sa.Column("department", sa.String(100), nullable=False),
        sa.Column("submitted_by", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("usage_frequency", sa.String(50), nullable=False),
        sa.Column("business_justification", sa.Text(), nullable=False),
        sa.Column("user_count_estimate", sa.Integer(), nullable=True),
        sa.Column("annual_cost_estimate", sa.Float(), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default=sa.text("'pending'")),
        sa.Column("matched_application_id", UUID(as_uuid=True), sa.ForeignKey("applications.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("submissions")
    op.drop_table("data_sources")
    op.drop_table("decisions")
    op.drop_table("recommendations")
    op.drop_table("applications")
