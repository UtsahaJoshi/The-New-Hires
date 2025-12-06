"""add_xp_and_level

Revision ID: c4bf4df94d79
Revises: 1c622b10b570
Create Date: 2025-12-06 01:38:08.102910

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c4bf4df94d79'
down_revision: Union[str, Sequence[str], None] = '1c622b10b570'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
