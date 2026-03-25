"""create messages table

Revision ID: f89482c5b3e8
Revises:
Create Date: 2025-10-08 02:00:08.259122

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "f89482c5b3e8"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "message",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("content", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("message")
