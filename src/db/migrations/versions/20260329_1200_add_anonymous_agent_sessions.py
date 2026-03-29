"""add anonymous_agent_sessions table

Revision ID: b8e4c91a2f70
Revises: 4d9a2ee8107b
Create Date: 2026-03-29

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import UUID

revision: str = "b8e4c91a2f70"
down_revision: Union[str, Sequence[str], None] = "4d9a2ee8107b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "anonymous_agent_sessions",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("interaction_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "config",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_anonymous_agent_sessions_token_hash"),
        "anonymous_agent_sessions",
        ["token_hash"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_anonymous_agent_sessions_token_hash"), table_name="anonymous_agent_sessions")
    op.drop_table("anonymous_agent_sessions")
