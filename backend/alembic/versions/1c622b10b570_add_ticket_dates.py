"""Add ticket dates

Revision ID: 1c622b10b570
Revises: 95bf950daf77
Create Date: 2025-12-06 01:07:38.167232

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1c622b10b570'
down_revision: Union[str, Sequence[str], None] = '95bf950daf77'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
