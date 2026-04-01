"""Add is_primary to data_sources, add data_sources.create permission

Revision ID: 009
Revises: 008
Create Date: 2025-01-01 00:00:00.000000

Adds the is_primary boolean flag for multi-source-per-type support and
a new data_sources.create permission for the add-source feature.
"""
from typing import Sequence, Union

import uuid

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "009"
down_revision: Union[str, None] = "008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

NS = uuid.UUID("a1b2c3d4-e5f6-7890-abcd-ef1234567890")


def _uuid(label: str) -> str:
    return str(uuid.uuid5(NS, label))


# Permission + role IDs
PERM_DS_CREATE = _uuid("perm-data_sources-create")
PERM_DS_DELETE = _uuid("perm-data_sources-delete")
ROLE_SUPER_ADMIN = _uuid("role-super-admin")
ROLE_ADMIN = _uuid("role-admin")


def upgrade() -> None:
    # 1. Add is_primary column
    op.add_column(
        "data_sources",
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default="false"),
    )

    # 2. Mark existing seeded sources as primary (they are the first of their type)
    op.execute(sa.text("UPDATE data_sources SET is_primary = true"))

    # 3. Add data_sources.create and data_sources.delete permissions
    op.execute(sa.text(
        f"INSERT INTO permissions (id, resource, action, description) VALUES "
        f"('{PERM_DS_CREATE}', 'data_sources', 'create', 'Create data sources'), "
        f"('{PERM_DS_DELETE}', 'data_sources', 'delete', 'Delete data sources')"
    ))

    # 4. Grant to Super Admin and Admin
    op.execute(sa.text(
        f"INSERT INTO role_permissions (role_id, permission_id) VALUES "
        f"('{ROLE_SUPER_ADMIN}', '{PERM_DS_CREATE}'), "
        f"('{ROLE_SUPER_ADMIN}', '{PERM_DS_DELETE}'), "
        f"('{ROLE_ADMIN}', '{PERM_DS_CREATE}'), "
        f"('{ROLE_ADMIN}', '{PERM_DS_DELETE}')"
    ))


def downgrade() -> None:
    # Remove permissions
    op.execute(sa.text(
        f"DELETE FROM role_permissions WHERE permission_id IN ('{PERM_DS_CREATE}', '{PERM_DS_DELETE}')"
    ))
    op.execute(sa.text(
        f"DELETE FROM permissions WHERE id IN ('{PERM_DS_CREATE}', '{PERM_DS_DELETE}')"
    ))
    # Drop column
    op.drop_column("data_sources", "is_primary")
