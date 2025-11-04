"""add_conference_chat_messages

Revision ID: fc4529133156
Revises: 1f576ec7b986
Create Date: 2025-11-01 16:08:07.001766

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'fc4529133156'
down_revision = '1f576ec7b986'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create conference_chat_messages table
    op.create_table('conference_chat_messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('conference_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('sender_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('message_type', sa.String(length=50), nullable=True),
        sa.Column('sender_name', sa.String(length=200), nullable=True),
        sa.Column('sender_role', sa.String(length=50), nullable=True),
        sa.Column('is_pinned', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('is_deleted', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('is_question', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('is_answered', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('likes_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('reply_to_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('sent_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('edited_at', sa.DateTime(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['conference_id'], ['video_conferences.id'], ),
        sa.ForeignKeyConstraint(['reply_to_id'], ['conference_chat_messages.id'], ),
        sa.ForeignKeyConstraint(['sender_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_conference_chat_messages_conference_id'), 'conference_chat_messages', ['conference_id'], unique=False)
    op.create_index(op.f('ix_conference_chat_messages_id'), 'conference_chat_messages', ['id'], unique=False)
    op.create_index(op.f('ix_conference_chat_messages_sender_id'), 'conference_chat_messages', ['sender_id'], unique=False)
    op.create_index(op.f('ix_conference_chat_messages_sent_at'), 'conference_chat_messages', ['sent_at'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_conference_chat_messages_sent_at'), table_name='conference_chat_messages')
    op.drop_index(op.f('ix_conference_chat_messages_sender_id'), table_name='conference_chat_messages')
    op.drop_index(op.f('ix_conference_chat_messages_id'), table_name='conference_chat_messages')
    op.drop_index(op.f('ix_conference_chat_messages_conference_id'), table_name='conference_chat_messages')
    op.drop_table('conference_chat_messages')
