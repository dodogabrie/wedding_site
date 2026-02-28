"""Add admin_notes to guests table.

Revision ID: 003
Revises: 002
Create Date: 2026-02-28
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_column(bind, table_name: str, column_name: str) -> bool:
    inspector = sa.inspect(bind)
    columns = {col["name"] for col in inspector.get_columns(table_name)}
    return column_name in columns


def upgrade() -> None:
    bind = op.get_bind()
    if not _has_column(bind, "guests", "admin_notes"):
        op.add_column("guests", sa.Column("admin_notes", sa.String(), nullable=True))


def downgrade() -> None:
    # SQLite doesn't support easy column drops, and it's safer to leave it if we ever roll back app code.
    pass
