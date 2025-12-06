"""Add user stats

Revision ID: 95bf950daf77
Revises: 02513c7c782e
Create Date: 2025-12-06 00:52:55.523198

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '95bf950daf77'
down_revision: Union[str, Sequence[str], None] = '02513c7c782e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Check if columns exist (simple approach: just add them, if fail, we assume they exist or handle error)
    # But better to use add_column safely. 
    # Since we know they are likely missing:
    op.add_column('users', sa.Column('xp', sa.Integer(), server_default='0', nullable=True))
    op.add_column('users', sa.Column('level', sa.Integer(), server_default='1', nullable=True))
    op.add_column('users', sa.Column('truthfulness', sa.Integer(), server_default='50', nullable=True))
    op.add_column('users', sa.Column('effort', sa.Integer(), server_default='50', nullable=True))
    op.add_column('users', sa.Column('reliability', sa.Integer(), server_default='50', nullable=True))
    op.add_column('users', sa.Column('collaboration', sa.Integer(), server_default='50', nullable=True))
    op.add_column('users', sa.Column('quality', sa.Integer(), server_default='50', nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'xp')
    op.drop_column('users', 'level')
    op.drop_column('users', 'truthfulness')
    op.drop_column('users', 'effort')
    op.drop_column('users', 'reliability')
    op.drop_column('users', 'collaboration')
    op.drop_column('users', 'quality')
