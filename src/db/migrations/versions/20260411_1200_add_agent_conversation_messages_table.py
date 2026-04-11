"""add agent_chat_history JSONB on anonymous sessions; agent_conversation_messages for sites

Revision ID: e2f3a4b5c6d7
Revises: b8e4c91a2f70
Create Date: 2026-04-11

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import UUID

revision: str = "e2f3a4b5c6d7"
down_revision: Union[str, Sequence[str], None] = "b8e4c91a2f70"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "anonymous_agent_sessions",
        sa.Column(
            "agent_chat_history",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
    )
    op.create_table(
        "agent_conversation_messages",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column("wedding_site_id", UUID(as_uuid=True), nullable=False),
        sa.Column("role", sa.String(length=16), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint(
            "role IN ('user', 'assistant')",
            name="ck_agent_conversation_messages_role",
        ),
        sa.ForeignKeyConstraint(
            ["wedding_site_id"],
            ["wedding_sites.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_agent_conversation_messages_wedding_site_id"),
        "agent_conversation_messages",
        ["wedding_site_id"],
        unique=False,
    )
    op.create_index(
        "ix_agent_conv_msg_site_created",
        "agent_conversation_messages",
        ["wedding_site_id", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_agent_conv_msg_site_created", table_name="agent_conversation_messages")
    op.drop_index(
        op.f("ix_agent_conversation_messages_wedding_site_id"),
        table_name="agent_conversation_messages",
    )
    op.drop_table("agent_conversation_messages")
    op.drop_column("anonymous_agent_sessions", "agent_chat_history")
