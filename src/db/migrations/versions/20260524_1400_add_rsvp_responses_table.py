"""add rsvp_responses table

Revision ID: b7c8d9e0f1a2
Revises: a1b2c3d4e5f6
Create Date: 2026-05-24

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "b7c8d9e0f1a2"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "rsvp_responses",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column("wedding_site_id", UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=254), nullable=True),
        sa.Column("phone", sa.String(length=20), nullable=True),
        sa.Column("is_attending", sa.Boolean(), nullable=False),
        sa.Column("party_size", sa.Integer(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["wedding_site_id"],
            ["wedding_sites.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "(is_attending IS TRUE AND party_size >= 1 AND party_size <= 10) "
            "OR (is_attending IS FALSE AND party_size = 0)",
            name="ck_rsvp_responses_attending_party_size",
        ),
    )
    op.create_index(
        op.f("ix_rsvp_responses_wedding_site_id"),
        "rsvp_responses",
        ["wedding_site_id"],
        unique=False,
    )
    op.create_index(
        "ix_rsvp_responses_wedding_site_id_created_at",
        "rsvp_responses",
        ["wedding_site_id", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_rsvp_responses_wedding_site_id_created_at",
        table_name="rsvp_responses",
    )
    op.drop_index(op.f("ix_rsvp_responses_wedding_site_id"), table_name="rsvp_responses")
    op.drop_table("rsvp_responses")
