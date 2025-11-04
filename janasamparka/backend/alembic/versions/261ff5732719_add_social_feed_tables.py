"""add_social_feed_tables

Revision ID: 261ff5732719
Revises: 24e6847939aa
Create Date: 2025-11-01 17:08:51.795807

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '261ff5732719'
down_revision = '24e6847939aa'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create social_posts table
    op.create_table('social_posts',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('author_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('author_name', sa.String(length=200), nullable=True),
        sa.Column('author_role', sa.String(length=50), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('post_type', sa.String(length=50), nullable=True, server_default='text'),
        sa.Column('has_media', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('media_urls', sa.Text(), nullable=True),
        sa.Column('media_types', sa.Text(), nullable=True),
        sa.Column('meeting_title', sa.String(length=500), nullable=True),
        sa.Column('meeting_date', sa.DateTime(), nullable=True),
        sa.Column('meeting_location', sa.String(length=500), nullable=True),
        sa.Column('meeting_link', sa.String(length=500), nullable=True),
        sa.Column('meeting_capacity', sa.Integer(), nullable=True),
        sa.Column('allow_public', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('likes_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('comments_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('shares_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('views_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('status', sa.String(length=50), nullable=True, server_default='published'),
        sa.Column('is_pinned', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('is_featured', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('constituency_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('is_global', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('tags', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('published_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['author_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['constituency_id'], ['constituencies.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_social_posts_author_id'), 'social_posts', ['author_id'], unique=False)
    op.create_index(op.f('ix_social_posts_constituency_id'), 'social_posts', ['constituency_id'], unique=False)
    op.create_index(op.f('ix_social_posts_created_at'), 'social_posts', ['created_at'], unique=False)
    op.create_index(op.f('ix_social_posts_id'), 'social_posts', ['id'], unique=False)
    op.create_index(op.f('ix_social_posts_is_pinned'), 'social_posts', ['is_pinned'], unique=False)
    op.create_index(op.f('ix_social_posts_post_type'), 'social_posts', ['post_type'], unique=False)
    op.create_index(op.f('ix_social_posts_published_at'), 'social_posts', ['published_at'], unique=False)
    op.create_index(op.f('ix_social_posts_status'), 'social_posts', ['status'], unique=False)

    # Create social_comments table
    op.create_table('social_comments',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('post_id', sa.String(), nullable=False),
        sa.Column('author_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('author_name', sa.String(length=200), nullable=True),
        sa.Column('author_role', sa.String(length=50), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('parent_comment_id', sa.String(), nullable=True),
        sa.Column('reply_level', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('is_approved', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('is_rejected', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('is_deleted', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('moderated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('moderated_at', sa.DateTime(), nullable=True),
        sa.Column('rejection_reason', sa.String(length=500), nullable=True),
        sa.Column('likes_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('edited_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['author_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['moderated_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['parent_comment_id'], ['social_comments.id'], ),
        sa.ForeignKeyConstraint(['post_id'], ['social_posts.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_social_comments_author_id'), 'social_comments', ['author_id'], unique=False)
    op.create_index(op.f('ix_social_comments_created_at'), 'social_comments', ['created_at'], unique=False)
    op.create_index(op.f('ix_social_comments_id'), 'social_comments', ['id'], unique=False)
    op.create_index(op.f('ix_social_comments_is_approved'), 'social_comments', ['is_approved'], unique=False)
    op.create_index(op.f('ix_social_comments_post_id'), 'social_comments', ['post_id'], unique=False)

    # Create social_likes table
    op.create_table('social_likes',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('post_id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['post_id'], ['social_posts.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_social_likes_id'), 'social_likes', ['id'], unique=False)
    op.create_index(op.f('ix_social_likes_post_id'), 'social_likes', ['post_id'], unique=False)
    op.create_index(op.f('ix_social_likes_user_id'), 'social_likes', ['user_id'], unique=False)

    # Create meeting_registrations table
    op.create_table('meeting_registrations',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('post_id', sa.String(), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('attendee_name', sa.String(length=200), nullable=False),
        sa.Column('attendee_phone', sa.String(length=15), nullable=True),
        sa.Column('attendee_email', sa.String(length=200), nullable=True),
        sa.Column('is_confirmed', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('is_attended', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('is_cancelled', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('registered_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('cancelled_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['post_id'], ['social_posts.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_meeting_registrations_id'), 'meeting_registrations', ['id'], unique=False)
    op.create_index(op.f('ix_meeting_registrations_post_id'), 'meeting_registrations', ['post_id'], unique=False)
    op.create_index(op.f('ix_meeting_registrations_user_id'), 'meeting_registrations', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_meeting_registrations_user_id'), table_name='meeting_registrations')
    op.drop_index(op.f('ix_meeting_registrations_post_id'), table_name='meeting_registrations')
    op.drop_index(op.f('ix_meeting_registrations_id'), table_name='meeting_registrations')
    op.drop_table('meeting_registrations')
    
    op.drop_index(op.f('ix_social_likes_user_id'), table_name='social_likes')
    op.drop_index(op.f('ix_social_likes_post_id'), table_name='social_likes')
    op.drop_index(op.f('ix_social_likes_id'), table_name='social_likes')
    op.drop_table('social_likes')
    
    op.drop_index(op.f('ix_social_comments_post_id'), table_name='social_comments')
    op.drop_index(op.f('ix_social_comments_is_approved'), table_name='social_comments')
    op.drop_index(op.f('ix_social_comments_id'), table_name='social_comments')
    op.drop_index(op.f('ix_social_comments_created_at'), table_name='social_comments')
    op.drop_index(op.f('ix_social_comments_author_id'), table_name='social_comments')
    op.drop_table('social_comments')
    
    op.drop_index(op.f('ix_social_posts_status'), table_name='social_posts')
    op.drop_index(op.f('ix_social_posts_published_at'), table_name='social_posts')
    op.drop_index(op.f('ix_social_posts_post_type'), table_name='social_posts')
    op.drop_index(op.f('ix_social_posts_is_pinned'), table_name='social_posts')
    op.drop_index(op.f('ix_social_posts_id'), table_name='social_posts')
    op.drop_index(op.f('ix_social_posts_created_at'), table_name='social_posts')
    op.drop_index(op.f('ix_social_posts_constituency_id'), table_name='social_posts')
    op.drop_index(op.f('ix_social_posts_author_id'), table_name='social_posts')
    op.drop_table('social_posts')
