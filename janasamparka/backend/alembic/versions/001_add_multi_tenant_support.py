"""Add multi-tenant support with constituencies

Revision ID: 001_multi_tenant
Revises: 
Create Date: 2025-10-27 18:28:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import geoalchemy2

# revision identifiers, used by Alembic.
revision = '001_multi_tenant'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create constituencies table
    op.create_table(
        'constituencies',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False, unique=True),
        sa.Column('code', sa.String(50), nullable=False, unique=True),
        sa.Column('district', sa.String(255), nullable=False),
        sa.Column('state', sa.String(100), nullable=False, server_default='Karnataka'),
        sa.Column('mla_name', sa.String(255)),
        sa.Column('mla_party', sa.String(100)),
        sa.Column('mla_contact_phone', sa.String(15)),
        sa.Column('mla_contact_email', sa.String(255)),
        sa.Column('total_population', sa.Integer, server_default='0'),
        sa.Column('total_wards', sa.Integer, server_default='0'),
        sa.Column('assembly_number', sa.Integer),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('subscription_tier', sa.String(50), server_default='basic'),
        sa.Column('description', sa.Text),
        sa.Column('logo_url', sa.String(500)),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
        sa.Column('activated_at', sa.DateTime)
    )
    
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('phone', sa.String(15), nullable=False, unique=True),
        sa.Column('role', sa.Enum('citizen', 'moderator', 'mla', 'department_officer', 'auditor', 'admin', 
                                   name='userrole'), nullable=False, server_default='citizen'),
        sa.Column('locale_pref', sa.String(5), server_default='kn'),
        sa.Column('is_active', sa.String(10), server_default='true'),
        sa.Column('constituency_id', postgresql.UUID(as_uuid=True)),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['constituency_id'], ['constituencies.id']),
    )
    op.create_index('ix_users_phone', 'users', ['phone'])
    op.create_index('ix_users_constituency', 'users', ['constituency_id'])
    
    # Create wards table with PostGIS
    op.create_table(
        'wards',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('ward_number', sa.Integer, nullable=False),
        sa.Column('taluk', sa.String(255), nullable=False),
        sa.Column('constituency_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('geom', geoalchemy2.Geometry('POLYGON', srid=4326)),
        sa.Column('population', sa.Integer, server_default='0'),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['constituency_id'], ['constituencies.id']),
    )
    op.create_index('ix_wards_constituency', 'wards', ['constituency_id'])
    op.create_index('ix_wards_geom', 'wards', ['geom'], postgresql_using='gist')
    
    # Create departments table
    op.create_table(
        'departments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('code', sa.String(50), nullable=False),
        sa.Column('constituency_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('contact_phone', sa.String(15)),
        sa.Column('contact_email', sa.String(255)),
        sa.Column('description', sa.String(500)),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['constituency_id'], ['constituencies.id']),
    )
    op.create_index('ix_departments_constituency', 'departments', ['constituency_id'])
    op.create_index('ix_departments_code_constituency', 'departments', ['code', 'constituency_id'], unique=True)
    
    # Create complaints table
    op.create_table(
        'complaints',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('constituency_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('description', sa.Text, nullable=False),
        sa.Column('category', sa.String(100)),
        sa.Column('lat', sa.Numeric(precision=10, scale=7)),
        sa.Column('lng', sa.Numeric(precision=10, scale=7)),
        sa.Column('ward_id', postgresql.UUID(as_uuid=True)),
        sa.Column('location_description', sa.String(500)),
        sa.Column('dept_id', postgresql.UUID(as_uuid=True)),
        sa.Column('assigned_to', postgresql.UUID(as_uuid=True)),
        sa.Column('status', sa.Enum('submitted', 'assigned', 'in_progress', 'resolved', 'closed', 'rejected',
                                     name='complaintstatus'), server_default='submitted'),
        sa.Column('priority', sa.Enum('low', 'medium', 'high', 'urgent',
                                       name='complaintpriority'), server_default='medium'),
        sa.Column('voice_transcript', sa.Text),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
        sa.Column('resolved_at', sa.DateTime),
        sa.Column('closed_at', sa.DateTime),
        sa.ForeignKeyConstraint(['constituency_id'], ['constituencies.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['ward_id'], ['wards.id']),
        sa.ForeignKeyConstraint(['dept_id'], ['departments.id']),
        sa.ForeignKeyConstraint(['assigned_to'], ['users.id']),
    )
    op.create_index('ix_complaints_constituency', 'complaints', ['constituency_id'])
    op.create_index('ix_complaints_user', 'complaints', ['user_id'])
    op.create_index('ix_complaints_status', 'complaints', ['status'])
    op.create_index('ix_complaints_created', 'complaints', ['created_at'])
    
    # Create media table
    op.create_table(
        'media',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('complaint_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('url', sa.String(500), nullable=False),
        sa.Column('media_type', sa.Enum('photo', 'video', 'audio', 'document', name='mediatype'), nullable=False),
        sa.Column('file_size', sa.Numeric),
        sa.Column('lat', sa.Numeric(precision=10, scale=7)),
        sa.Column('lng', sa.Numeric(precision=10, scale=7)),
        sa.Column('proof_type', sa.String(20)),
        sa.Column('uploaded_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
        sa.Column('uploaded_by', postgresql.UUID(as_uuid=True)),
        sa.ForeignKeyConstraint(['complaint_id'], ['complaints.id']),
        sa.ForeignKeyConstraint(['uploaded_by'], ['users.id']),
    )
    op.create_index('ix_media_complaint', 'media', ['complaint_id'])
    
    # Create status_logs table
    op.create_table(
        'status_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('complaint_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('old_status', sa.String(50)),
        sa.Column('new_status', sa.String(50), nullable=False),
        sa.Column('changed_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('note', sa.Text),
        sa.Column('timestamp', sa.DateTime, nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['complaint_id'], ['complaints.id']),
        sa.ForeignKeyConstraint(['changed_by'], ['users.id']),
    )
    op.create_index('ix_status_logs_complaint', 'status_logs', ['complaint_id'])
    
    # Create polls table
    op.create_table(
        'polls',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('constituency_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('ward_id', postgresql.UUID(as_uuid=True)),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('start_date', sa.DateTime, nullable=False, server_default=sa.text('now()')),
        sa.Column('end_date', sa.DateTime, nullable=False),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['constituency_id'], ['constituencies.id']),
        sa.ForeignKeyConstraint(['ward_id'], ['wards.id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
    )
    op.create_index('ix_polls_constituency', 'polls', ['constituency_id'])
    
    # Create poll_options table
    op.create_table(
        'poll_options',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('poll_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('option_text', sa.String(500), nullable=False),
        sa.Column('vote_count', sa.Integer, server_default='0'),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['poll_id'], ['polls.id']),
    )
    op.create_index('ix_poll_options_poll', 'poll_options', ['poll_id'])
    
    # Create votes table
    op.create_table(
        'votes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('poll_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('option_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('voted_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['poll_id'], ['polls.id']),
        sa.ForeignKeyConstraint(['option_id'], ['poll_options.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.UniqueConstraint('poll_id', 'user_id', name='uq_poll_user_vote')
    )
    op.create_index('ix_votes_poll', 'votes', ['poll_id'])
    op.create_index('ix_votes_user', 'votes', ['user_id'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('votes')
    op.drop_table('poll_options')
    op.drop_table('polls')
    op.drop_table('status_logs')
    op.drop_table('media')
    op.drop_table('complaints')
    op.drop_table('departments')
    op.drop_table('wards')
    op.drop_table('users')
    op.drop_table('constituencies')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS userrole')
    op.execute('DROP TYPE IF EXISTS complaintstatus')
    op.execute('DROP TYPE IF EXISTS complaintpriority')
    op.execute('DROP TYPE IF EXISTS mediatype')
