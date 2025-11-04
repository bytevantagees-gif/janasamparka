"""add_knowledge_forum_tables

Revision ID: 24e6847939aa
Revises: ace353a81598
Create Date: 2025-11-01 16:45:24.240798

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '24e6847939aa'
down_revision = 'ace353a81598'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create forum_topics table
    op.create_table('forum_topics',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('author_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('author_name', sa.String(length=200), nullable=True),
        sa.Column('author_role', sa.String(length=50), nullable=True),
        sa.Column('constituency_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('complaint_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('gram_panchayat_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True, server_default='open'),
        sa.Column('is_pinned', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('is_featured', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('is_moderated', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('is_public', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('allowed_roles', sa.Text(), nullable=True),
        sa.Column('tags', sa.Text(), nullable=True),
        sa.Column('views_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('replies_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('likes_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('last_activity_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('closed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['author_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['constituency_id'], ['constituencies.id'], ),
        sa.ForeignKeyConstraint(['complaint_id'], ['complaints.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_forum_topics_author_id'), 'forum_topics', ['author_id'], unique=False)
    op.create_index(op.f('ix_forum_topics_category'), 'forum_topics', ['category'], unique=False)
    op.create_index(op.f('ix_forum_topics_constituency_id'), 'forum_topics', ['constituency_id'], unique=False)
    op.create_index(op.f('ix_forum_topics_created_at'), 'forum_topics', ['created_at'], unique=False)
    op.create_index(op.f('ix_forum_topics_id'), 'forum_topics', ['id'], unique=False)
    op.create_index(op.f('ix_forum_topics_is_pinned'), 'forum_topics', ['is_pinned'], unique=False)
    op.create_index(op.f('ix_forum_topics_last_activity_at'), 'forum_topics', ['last_activity_at'], unique=False)
    op.create_index(op.f('ix_forum_topics_status'), 'forum_topics', ['status'], unique=False)
    op.create_index(op.f('ix_forum_topics_title'), 'forum_topics', ['title'], unique=False)

    # Create forum_posts table
    op.create_table('forum_posts',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('topic_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('author_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('author_name', sa.String(length=200), nullable=True),
        sa.Column('author_role', sa.String(length=50), nullable=True),
        sa.Column('parent_post_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('reply_level', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('is_approved', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('is_deleted', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('moderated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('moderated_at', sa.DateTime(), nullable=True),
        sa.Column('is_solution', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('is_helpful', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('likes_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('has_attachments', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('attachment_urls', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('edited_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['author_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['moderated_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['parent_post_id'], ['forum_posts.id'], ),
        sa.ForeignKeyConstraint(['topic_id'], ['forum_topics.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_forum_posts_author_id'), 'forum_posts', ['author_id'], unique=False)
    op.create_index(op.f('ix_forum_posts_created_at'), 'forum_posts', ['created_at'], unique=False)
    op.create_index(op.f('ix_forum_posts_id'), 'forum_posts', ['id'], unique=False)
    op.create_index(op.f('ix_forum_posts_is_approved'), 'forum_posts', ['is_approved'], unique=False)
    op.create_index(op.f('ix_forum_posts_topic_id'), 'forum_posts', ['topic_id'], unique=False)

    # Create forum_likes table
    op.create_table('forum_likes',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('topic_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('post_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['post_id'], ['forum_posts.id'], ),
        sa.ForeignKeyConstraint(['topic_id'], ['forum_topics.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_forum_likes_id'), 'forum_likes', ['id'], unique=False)
    op.create_index(op.f('ix_forum_likes_post_id'), 'forum_likes', ['post_id'], unique=False)
    op.create_index(op.f('ix_forum_likes_topic_id'), 'forum_likes', ['topic_id'], unique=False)
    op.create_index(op.f('ix_forum_likes_user_id'), 'forum_likes', ['user_id'], unique=False)

    # Create forum_subscriptions table
    op.create_table('forum_subscriptions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('topic_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('notify_on_reply', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('notify_on_solution', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['topic_id'], ['forum_topics.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_forum_subscriptions_id'), 'forum_subscriptions', ['id'], unique=False)
    op.create_index(op.f('ix_forum_subscriptions_topic_id'), 'forum_subscriptions', ['topic_id'], unique=False)
    op.create_index(op.f('ix_forum_subscriptions_user_id'), 'forum_subscriptions', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_forum_subscriptions_user_id'), table_name='forum_subscriptions')
    op.drop_index(op.f('ix_forum_subscriptions_topic_id'), table_name='forum_subscriptions')
    op.drop_index(op.f('ix_forum_subscriptions_id'), table_name='forum_subscriptions')
    op.drop_table('forum_subscriptions')
    
    op.drop_index(op.f('ix_forum_likes_user_id'), table_name='forum_likes')
    op.drop_index(op.f('ix_forum_likes_topic_id'), table_name='forum_likes')
    op.drop_index(op.f('ix_forum_likes_post_id'), table_name='forum_likes')
    op.drop_index(op.f('ix_forum_likes_id'), table_name='forum_likes')
    op.drop_table('forum_likes')
    
    op.drop_index(op.f('ix_forum_posts_topic_id'), table_name='forum_posts')
    op.drop_index(op.f('ix_forum_posts_is_approved'), table_name='forum_posts')
    op.drop_index(op.f('ix_forum_posts_id'), table_name='forum_posts')
    op.drop_index(op.f('ix_forum_posts_created_at'), table_name='forum_posts')
    op.drop_index(op.f('ix_forum_posts_author_id'), table_name='forum_posts')
    op.drop_table('forum_posts')
    
    op.drop_index(op.f('ix_forum_topics_title'), table_name='forum_topics')
    op.drop_index(op.f('ix_forum_topics_status'), table_name='forum_topics')
    op.drop_index(op.f('ix_forum_topics_last_activity_at'), table_name='forum_topics')
    op.drop_index(op.f('ix_forum_topics_is_pinned'), table_name='forum_topics')
    op.drop_index(op.f('ix_forum_topics_id'), table_name='forum_topics')
    op.drop_index(op.f('ix_forum_topics_created_at'), table_name='forum_topics')
    op.drop_index(op.f('ix_forum_topics_constituency_id'), table_name='forum_topics')
    op.drop_index(op.f('ix_forum_topics_category'), table_name='forum_topics')
    op.drop_index(op.f('ix_forum_topics_author_id'), table_name='forum_topics')
    op.drop_table('forum_topics')
