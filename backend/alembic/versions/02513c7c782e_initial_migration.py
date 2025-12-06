"""Initial migration

Revision ID: 02513c7c782e
Revises: 
Create Date: 2025-12-05 15:18:18.600395

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '02513c7c782e'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # USERS
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('github_id', sa.String(), nullable=True),
        sa.Column('username', sa.String(), nullable=True),
        sa.Column('avatar_url', sa.String(), nullable=True),
        sa.Column('access_token', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_github_id'), 'users', ['github_id'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)

    # TICKETS
    op.create_table('tickets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('type', sa.String(), nullable=True),
        sa.Column('priority', sa.Enum('LOW', 'MEDIUM', 'HIGH', 'CRITICAL', name='ticketpriority'), nullable=True),
        sa.Column('story_points', sa.Integer(), nullable=True),
        sa.Column('status', sa.Enum('BACKLOG', 'TODO', 'IN_PROGRESS', 'CODE_REVIEW', 'DONE', name='ticketstatus'), nullable=True),
        sa.Column('assignee_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('due_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['assignee_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tickets_id'), 'tickets', ['id'], unique=False)
    op.create_index(op.f('ix_tickets_title'), 'tickets', ['title'], unique=False)

    # MESSAGES
    op.create_table('messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('channel', sa.String(), nullable=True),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('sender_id', sa.Integer(), nullable=True),
        sa.Column('is_bot', sa.Boolean(), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['sender_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_messages_channel'), 'messages', ['channel'], unique=False)
    op.create_index(op.f('ix_messages_id'), 'messages', ['id'], unique=False)

    # SESSIONS, SHADOWS, ETC (Just Standups for MVP)
    op.create_table('standups',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('audio_url', sa.String(), nullable=True),
        sa.Column('date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('is_completed', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_standups_id'), 'standups', ['id'], unique=False)
    
    # RETROSPECTIVES
    op.create_table('retrospectives',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('video_url', sa.String(), nullable=True),
        sa.Column('consent_given', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_retrospectives_id'), 'retrospectives', ['id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_retrospectives_id'), table_name='retrospectives')
    op.drop_table('retrospectives')
    op.drop_index(op.f('ix_standups_id'), table_name='standups')
    op.drop_table('standups')
    op.drop_index(op.f('ix_messages_id'), table_name='messages')
    op.drop_index(op.f('ix_messages_channel'), table_name='messages')
    op.drop_table('messages')
    op.drop_index(op.f('ix_tickets_title'), table_name='tickets')
    op.drop_index(op.f('ix_tickets_id'), table_name='tickets')
    op.drop_table('tickets')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_github_id'), table_name='users')
    op.drop_table('users')
