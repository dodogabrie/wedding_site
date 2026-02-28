"""Create photos and vote_audits tables.

Revision ID: 004
Revises: 003
Create Date: 2026-02-28
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_table(bind, table_name: str) -> bool:
    inspector = sa.inspect(bind)
    return table_name in inspector.get_table_names()


def _has_index(bind, table_name: str, index_name: str) -> bool:
    inspector = sa.inspect(bind)
    indexes = {index["name"] for index in inspector.get_indexes(table_name)}
    return index_name in indexes


def upgrade() -> None:
    bind = op.get_bind()

    if not _has_table(bind, "photos"):
        op.create_table(
            "photos",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("original_filename", sa.String(), nullable=False),
            sa.Column("uploader_name", sa.String(), nullable=True),
            sa.Column("caption", sa.String(), nullable=True),
            sa.Column("mime_type", sa.String(), nullable=False),
            sa.Column("file_size", sa.Integer(), nullable=False),
            sa.Column("width", sa.Integer(), nullable=True),
            sa.Column("height", sa.Integer(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )

    if not _has_table(bind, "vote_audits"):
        op.create_table(
            "vote_audits",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("ip_address", sa.String(), nullable=False),
            sa.Column("scope_type", sa.String(), nullable=False),
            sa.Column("scope_id", sa.Integer(), nullable=False),
            sa.Column("guest_id", sa.Integer(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(["guest_id"], ["guests.id"]),
            sa.PrimaryKeyConstraint("id"),
        )

    if _has_table(bind, "vote_audits") and not _has_index(bind, "vote_audits", "ix_vote_audits_id"):
        op.create_index("ix_vote_audits_id", "vote_audits", ["id"], unique=False)

    if _has_table(bind, "vote_audits") and not _has_index(bind, "vote_audits", "ix_vote_audits_ip_address"):
        op.create_index("ix_vote_audits_ip_address", "vote_audits", ["ip_address"], unique=False)


def downgrade() -> None:
    # Keep tables in place on SQLite; dropping them is unnecessary and potentially destructive.
    pass
