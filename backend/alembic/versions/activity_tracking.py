"""add activity table

Revision ID: activity_tracking
Revises: 95bf950daf77
Create Date: 2025-12-06

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'activity_tracking'
down_revision = 'c4bf4df94d79'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('activities',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('activity_type', sa.Enum('TICKET_ASSIGNED', 'TICKET_COMPLETED', 'MESSAGE_SENT', 'MESSAGE_RECEIVED', 'REPO_CREATED', 'STANDUP_COMPLETED', 'CODE_REVIEW_SUBMITTED', 'ACHIEVEMENT_EARNED', name='activitytype'), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('extra_data', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_activities_id'), 'activities', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_activities_id'), table_name='activities')
    op.drop_table('activities')
