"""add wedding_sites table

Revision ID: 4d9a2ee8107b
Revises: 7c2a9f1b4d60
Create Date: 2026-03-25

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import UUID

revision: str = "4d9a2ee8107b"
down_revision: Union[str, Sequence[str], None] = "7c2a9f1b4d60"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "wedding_sites",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column("owner_user_id", UUID(as_uuid=True), nullable=False),
        sa.Column("slug", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column(
            "config",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("schema_version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_wedding_sites_owner_user_id"), "wedding_sites", ["owner_user_id"], unique=False)
    op.create_index(op.f("ix_wedding_sites_slug"), "wedding_sites", ["slug"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_wedding_sites_slug"), table_name="wedding_sites")
    op.drop_index(op.f("ix_wedding_sites_owner_user_id"), table_name="wedding_sites")
    op.drop_table("wedding_sites")
