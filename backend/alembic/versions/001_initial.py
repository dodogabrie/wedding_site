"""Initial migration - create families and guests tables

Revision ID: 001
Revises:
Create Date: 2026-01-28

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'families',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('family_name', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_families_id'), 'families', ['id'], unique=False)

    op.create_table(
        'guests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('family_id', sa.Integer(), nullable=True),
        sa.Column('attending', sa.Boolean(), nullable=True),
        sa.Column('dietary_notes', sa.String(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['family_id'], ['families.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_guests_id'), 'guests', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_guests_id'), table_name='guests')
    op.drop_table('guests')
    op.drop_index(op.f('ix_families_id'), table_name='families')
    op.drop_table('families')
