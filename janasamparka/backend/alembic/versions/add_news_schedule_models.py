"""Add news, schedule, and ticker models

Revision ID: add_news_schedule_models
Revises: add_performance_indexes
Create Date: 2024-01-01 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_news_schedule_models'
down_revision = 'add_performance_indexes'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create news, schedule, and ticker tables"""
    
    # Create news table
    op.create_table('news',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=sa.text('gen_random_uuid()')),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('summary', sa.String(length=1000), nullable=True),
        sa.Column('category', sa.Enum('LOCAL_DEVELOPMENT', 'GOVERNMENT_INITIATIVE', 'PUBLIC_SERVICE', 'MEETING', 'ACHIEVEMENT', 'ANNOUNCEMENT', 'EMERGENCY', 'OTHER', name='newscategory'), nullable=False),
        sa.Column('priority', sa.Enum('LOW', 'MEDIUM', 'HIGH', 'URGENT', name='newspriority'), nullable=True),
        sa.Column('constituency_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('mla_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('featured_image_url', sa.String(length=500), nullable=True),
        sa.Column('image_urls', sa.Text(), nullable=True),
        sa.Column('is_published', sa.Boolean(), nullable=True),
        sa.Column('is_featured', sa.Boolean(), nullable=True),
        sa.Column('show_in_ticker', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('published_at', sa.DateTime(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('source', sa.String(length=200), nullable=True),
        sa.Column('author', sa.String(length=200), nullable=True),
        sa.Column('tags', sa.Text(), nullable=True),
        sa.Column('view_count', sa.Integer(), nullable=True),
        sa.Column('is_archived', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['constituency_id'], ['constituencies.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['mla_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_news_category'), 'news', ['category'], unique=False)
    op.create_index(op.f('ix_news_constituency_id'), 'news', ['constituency_id'], unique=False)
    op.create_index(op.f('ix_news_created_at'), 'news', ['created_at'], unique=False)
    op.create_index(op.f('ix_news_id'), 'news', ['id'], unique=True)
    op.create_index(op.f('ix_news_is_archived'), 'news', ['is_archived'], unique=False)
    op.create_index(op.f('ix_news_is_featured'), 'news', ['is_featured'], unique=False)
    op.create_index(op.f('ix_news_is_published'), 'news', ['is_published'], unique=False)
    op.create_index(op.f('ix_news_mla_id'), 'news', ['mla_id'], unique=False)
    op.create_index(op.f('ix_news_priority'), 'news', ['priority'], unique=False)
    
    # Create mla_schedules table
    op.create_table('mla_schedules',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=sa.text('gen_random_uuid()')),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('mla_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('constituency_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('schedule_type', sa.Enum('MEETING', 'PUBLIC_EVENT', 'OFFICE_HOURS', 'CAMP', 'INSPECTION', 'PRESS_CONFERENCE', 'OTHER', name='scheduletype'), nullable=False),
        sa.Column('status', sa.Enum('SCHEDULED', 'CANCELLED', 'COMPLETED', 'POSTPONED', name='schedulestatus'), nullable=True),
        sa.Column('venue', sa.String(length=500), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('latitude', sa.String(length=50), nullable=True),
        sa.Column('longitude', sa.String(length=50), nullable=True),
        sa.Column('start_datetime', sa.DateTime(), nullable=False),
        sa.Column('end_datetime', sa.DateTime(), nullable=False),
        sa.Column('is_all_day', sa.Boolean(), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=True),
        sa.Column('is_featured', sa.Boolean(), nullable=True),
        sa.Column('expected_attendees', sa.Integer(), nullable=True),
        sa.Column('max_attendees', sa.Integer(), nullable=True),
        sa.Column('registration_required', sa.Boolean(), nullable=True),
        sa.Column('contact_person', sa.String(length=200), nullable=True),
        sa.Column('contact_phone', sa.String(length=20), nullable=True),
        sa.Column('contact_email', sa.String(length=200), nullable=True),
        sa.Column('agenda', sa.Text(), nullable=True),
        sa.Column('requirements', sa.Text(), nullable=True),
        sa.Column('external_links', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('reminder_sent', sa.Boolean(), nullable=True),
        sa.Column('reminder_minutes_before', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['constituency_id'], ['constituencies.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['mla_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_mla_schedules_constituency_id'), 'mla_schedules', ['constituency_id'], unique=False)
    op.create_index(op.f('ix_mla_schedules_created_at'), 'mla_schedules', ['created_at'], unique=False)
    op.create_index(op.f('ix_mla_schedules_end_datetime'), 'mla_schedules', ['end_datetime'], unique=False)
    op.create_index(op.f('ix_mla_schedules_id'), 'mla_schedules', ['id'], unique=True)
    op.create_index(op.f('ix_mla_schedules_is_featured'), 'mla_schedules', ['is_featured'], unique=False)
    op.create_index(op.f('ix_mla_schedules_is_public'), 'mla_schedules', ['is_public'], unique=False)
    op.create_index(op.f('ix_mla_schedules_mla_id'), 'mla_schedules', ['mla_id'], unique=False)
    op.create_index(op.f('ix_mla_schedules_schedule_type'), 'mla_schedules', ['schedule_type'], unique=False)
    op.create_index(op.f('ix_mla_schedules_start_datetime'), 'mla_schedules', ['start_datetime'], unique=False)
    op.create_index(op.f('ix_mla_schedules_status'), 'mla_schedules', ['status'], unique=False)
    
    # Create ticker_items table
    op.create_table('ticker_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=sa.text('gen_random_uuid()')),
        sa.Column('content', sa.String(length=500), nullable=False),
        sa.Column('content_type', sa.String(length=50), nullable=True),
        sa.Column('constituency_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('mla_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('related_item_type', sa.String(length=50), nullable=True),
        sa.Column('related_item_id', sa.String(length=50), nullable=True),
        sa.Column('priority', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('start_time', sa.DateTime(), nullable=True),
        sa.Column('end_time', sa.DateTime(), nullable=True),
        sa.Column('background_color', sa.String(length=20), nullable=True),
        sa.Column('text_color', sa.String(length=20), nullable=True),
        sa.Column('icon', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['constituency_id'], ['constituencies.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['mla_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ticker_items_created_at'), 'ticker_items', ['created_at'], unique=False)
    op.create_index(op.f('ix_ticker_items_id'), 'ticker_items', ['id'], unique=True)
    op.create_index(op.f('ix_ticker_items_is_active'), 'ticker_items', ['is_active'], unique=False)
    op.create_index(op.f('ix_ticker_items_mla_id'), 'ticker_items', ['mla_id'], unique=False)
    op.create_index(op.f('ix_ticker_items_constituency_id'), 'ticker_items', ['constituency_id'], unique=False)


def downgrade() -> None:
    """Drop news, schedule, and ticker tables"""
    
    # Drop ticker_items table
    op.drop_index(op.f('ix_ticker_items_constituency_id'), table_name='ticker_items')
    op.drop_index(op.f('ix_ticker_items_mla_id'), table_name='ticker_items')
    op.drop_index(op.f('ix_ticker_items_is_active'), table_name='ticker_items')
    op.drop_index(op.f('ix_ticker_items_id'), table_name='ticker_items')
    op.drop_index(op.f('ix_ticker_items_created_at'), table_name='ticker_items')
    op.drop_table('ticker_items')
    
    # Drop mla_schedules table
    op.drop_index(op.f('ix_mla_schedules_status'), table_name='mla_schedules')
    op.drop_index(op.f('ix_mla_schedules_start_datetime'), table_name='mla_schedules')
    op.drop_index(op.f('ix_mla_schedules_schedule_type'), table_name='mla_schedules')
    op.drop_index(op.f('ix_mla_schedules_mla_id'), table_name='mla_schedules')
    op.drop_index(op.f('ix_mla_schedules_is_public'), table_name='mla_schedules')
    op.drop_index(op.f('ix_mla_schedules_is_featured'), table_name='mla_schedules')
    op.drop_index(op.f('ix_mla_schedules_end_datetime'), table_name='mla_schedules')
    op.drop_index(op.f('ix_mla_schedules_id'), table_name='mla_schedules')
    op.drop_index(op.f('ix_mla_schedules_created_at'), table_name='mla_schedules')
    op.drop_index(op.f('ix_mla_schedules_constituency_id'), table_name='mla_schedules')
    op.drop_table('mla_schedules')
    
    # Drop news table
    op.drop_index(op.f('ix_news_priority'), table_name='news')
    op.drop_index(op.f('ix_news_mla_id'), table_name='news')
    op.drop_index(op.f('ix_news_is_published'), table_name='news')
    op.drop_index(op.f('ix_news_is_featured'), table_name='news')
    op.drop_index(op.f('ix_news_is_archived'), table_name='news')
    op.drop_index(op.f('ix_news_id'), table_name='news')
    op.drop_index(op.f('ix_news_created_at'), table_name='news')
    op.drop_index(op.f('ix_news_constituency_id'), table_name='news')
    op.drop_index(op.f('ix_news_category'), table_name='news')
    op.drop_table('news')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS newscategory')
    op.execute('DROP TYPE IF EXISTS newspaperpriority')
    op.execute('DROP TYPE IF EXISTS scheduletype')
    op.execute('DROP TYPE IF EXISTS schedulestatus')
