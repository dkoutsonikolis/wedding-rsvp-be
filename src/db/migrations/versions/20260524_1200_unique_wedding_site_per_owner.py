"""unique wedding site per owner

Revision ID: a1b2c3d4e5f6
Revises: f3b7d9a1c2e4
Create Date: 2026-05-24

"""
from typing import Sequence, Union

from alembic import op

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "f3b7d9a1c2e4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_index(op.f("ix_wedding_sites_owner_user_id"), table_name="wedding_sites")
    op.create_index(
        op.f("ix_wedding_sites_owner_user_id"),
        "wedding_sites",
        ["owner_user_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_wedding_sites_owner_user_id"), table_name="wedding_sites")
    op.create_index(
        op.f("ix_wedding_sites_owner_user_id"),
        "wedding_sites",
        ["owner_user_id"],
        unique=False,
    )
