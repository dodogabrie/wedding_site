"""Add per-event RSVP fields and allergens storage.

Revision ID: 002
Revises: 001
Create Date: 2026-02-26
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_column(bind, table_name: str, column_name: str) -> bool:
    inspector = sa.inspect(bind)
    columns = {col["name"] for col in inspector.get_columns(table_name)}
    return column_name in columns


def upgrade() -> None:
    bind = op.get_bind()

    if not _has_column(bind, "guests", "attendance_choice"):
        op.add_column("guests", sa.Column("attendance_choice", sa.String(), nullable=True))

    if not _has_column(bind, "guests", "attend_ceremony"):
        op.add_column("guests", sa.Column("attend_ceremony", sa.Boolean(), nullable=True))

    if not _has_column(bind, "guests", "attend_lunch"):
        op.add_column("guests", sa.Column("attend_lunch", sa.Boolean(), nullable=True))

    if not _has_column(bind, "guests", "allergens"):
        op.add_column("guests", sa.Column("allergens", sa.JSON(), nullable=True))

    # Backfill from legacy single-choice field if present.
    if _has_column(bind, "guests", "attendance_choice"):
        op.execute(
            sa.text(
                """
                UPDATE guests
                SET
                  attend_ceremony = CASE
                    WHEN attendance_choice = 'ceremony' THEN 1
                    WHEN attendance_choice = 'lunch' THEN 0
                    WHEN attendance_choice = 'decline' THEN 0
                    ELSE attend_ceremony
                  END,
                  attend_lunch = CASE
                    WHEN attendance_choice = 'ceremony' THEN 0
                    WHEN attendance_choice = 'lunch' THEN 1
                    WHEN attendance_choice = 'decline' THEN 0
                    ELSE attend_lunch
                  END
                WHERE attendance_choice IS NOT NULL
                  AND (attend_ceremony IS NULL OR attend_lunch IS NULL)
                """
            )
        )

    # Backfill remaining rows from legacy boolean.
    # Heuristic: historical "attending = true" becomes ceremony=yes, lunch=yes
    # so existing positive RSVPs remain positive for both events by default.
    op.execute(
        sa.text(
            """
            UPDATE guests
            SET
              attend_ceremony = CASE
                WHEN attend_ceremony IS NULL AND attending = 1 THEN 1
                WHEN attend_ceremony IS NULL AND attending = 0 THEN 0
                ELSE attend_ceremony
              END,
              attend_lunch = CASE
                WHEN attend_lunch IS NULL AND attending = 1 THEN 1
                WHEN attend_lunch IS NULL AND attending = 0 THEN 0
                ELSE attend_lunch
              END
            """
        )
    )


def downgrade() -> None:
    # SQLite column drops are destructive and not needed for this project flow.
    pass

