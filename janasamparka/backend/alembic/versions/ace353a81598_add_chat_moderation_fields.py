"""add_chat_moderation_fields

Revision ID: ace353a81598
Revises: fc4529133156
Create Date: 2025-11-01 16:11:53.608837

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'ace353a81598'
down_revision = 'fc4529133156'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add moderation fields to conference_chat_messages
    op.add_column('conference_chat_messages', sa.Column('is_approved', sa.Boolean(), server_default='false', nullable=True))
    op.add_column('conference_chat_messages', sa.Column('is_rejected', sa.Boolean(), server_default='false', nullable=True))
    op.add_column('conference_chat_messages', sa.Column('moderated_by', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('conference_chat_messages', sa.Column('moderated_at', sa.DateTime(), nullable=True))
    op.add_column('conference_chat_messages', sa.Column('rejection_reason', sa.String(length=500), nullable=True))
    
    # Add indexes
    op.create_index(op.f('ix_conference_chat_messages_is_approved'), 'conference_chat_messages', ['is_approved'], unique=False)
    
    # Add foreign key for moderator
    op.create_foreign_key('conference_chat_messages_moderated_by_fkey', 'conference_chat_messages', 'users', ['moderated_by'], ['id'])


def downgrade() -> None:
    op.drop_constraint('conference_chat_messages_moderated_by_fkey', 'conference_chat_messages', type_='foreignkey')
    op.drop_index(op.f('ix_conference_chat_messages_is_approved'), table_name='conference_chat_messages')
    op.drop_column('conference_chat_messages', 'rejection_reason')
    op.drop_column('conference_chat_messages', 'moderated_at')
    op.drop_column('conference_chat_messages', 'moderated_by')
    op.drop_column('conference_chat_messages', 'is_rejected')
    op.drop_column('conference_chat_messages', 'is_approved')
