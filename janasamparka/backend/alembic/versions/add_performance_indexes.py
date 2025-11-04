"""Add performance indexes

Revision ID: add_performance_indexes
Revises: eea1551a83eb
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_performance_indexes'
down_revision = 'eea1551a83eb'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add performance indexes for optimized queries"""
    
    # Complaints table indexes
    # Primary query patterns: by status, by constituency, by user, by date
    op.create_index('idx_complaints_status_priority', 'complaints', 
                   ['status', 'priority'], unique=False)
    
    op.create_index('idx_complaints_constituency_status', 'complaints', 
                   ['constituency_id', 'status'], unique=False)
    
    op.create_index('idx_complaints_user_created', 'complaints', 
                   ['user_id', 'created_at'], unique=False)
    
    op.create_index('idx_complaints_department_status', 'complaints', 
                   ['dept_id', 'status'], unique=False)
    
    op.create_index('idx_complaints_created_at_desc', 'complaints', 
                   ['created_at'], unique=False)
    
    op.create_index('idx_complaints_last_activity_desc', 'complaints', 
                   ['last_activity_at'], unique=False)
    
    op.create_index('idx_complaints_category_status', 'complaints', 
                   ['category', 'status'], unique=False)
    
    op.create_index('idx_complaints_urgent_priority', 'complaints', 
                   ['priority'], unique=False, 
                   postgresql_where=sa.text("priority = 'urgent'"))
    
    # Location-based queries
    op.create_index('idx_complaints_location', 'complaints', 
                   ['lat', 'lng'], unique=False)
    
    # Users table indexes
    op.create_index('idx_users_phone_unique', 'users', 
                   ['phone'], unique=True)
    
    op.create_index('idx_users_email_unique', 'users', 
                   ['email'], unique=True)
    
    op.create_index('idx_users_constituency_role', 'users', 
                   ['constituency_id', 'role'], unique=False)
    
    op.create_index('idx_users_active_verified', 'users', 
                   ['is_active', 'is_verified'], unique=False)
    
    # Departments table indexes
    op.create_index('idx_departments_constituency_active', 'departments', 
                   ['constituency_id', 'is_active'], unique=False)
    
    # Wards table indexes
    op.create_index('idx_wards_constituency_number', 'wards', 
                   ['constituency_id', 'ward_number'], unique=False)
    
    # Status logs indexes
    op.create_index('idx_status_logs_complaint_timestamp', 'status_logs', 
                   ['complaint_id', 'timestamp'], unique=False)
    
    op.create_index('idx_status_logs_changed_by_timestamp', 'status_logs', 
                   ['changed_by', 'timestamp'], unique=False)
    
    # Media table indexes
    op.create_index('idx_media_complaint_type', 'media', 
                   ['complaint_id', 'media_type'], unique=False)
    
    op.create_index('idx_media_uploaded_at', 'media', 
                   ['uploaded_at'], unique=False)
    
    # Constituency indexes
    op.create_index('idx_constituencies_active', 'constituencies', 
                   ['is_active'], unique=False)
    
    # Composite indexes for common API queries
    op.create_index('idx_complaints_api_list', 'complaints', 
                   ['constituency_id', 'status', 'created_at'], unique=False)
    
    op.create_index('idx_complaints_analytics', 'complaints', 
                   ['status', 'priority', 'created_at'], unique=False)
    
    # JSON indexes for Postgres (if using JSON columns)
    # Note: These would be added if we had JSON columns for metadata
    # op.create_index('idx_complaints_metadata_gin', 'complaints', 
    #                ['metadata'], unique=False, postgresql_using='gin')


def downgrade() -> None:
    """Remove performance indexes"""
    
    # Complaints table indexes
    op.drop_index('idx_complaints_status_priority', table_name='complaints')
    op.drop_index('idx_complaints_constituency_status', table_name='complaints')
    op.drop_index('idx_complaints_user_created', table_name='complaints')
    op.drop_index('idx_complaints_department_status', table_name='complaints')
    op.drop_index('idx_complaints_created_at_desc', table_name='complaints')
    op.drop_index('idx_complaints_last_activity_desc', table_name='complaints')
    op.drop_index('idx_complaints_category_status', table_name='complaints')
    op.drop_index('idx_complaints_urgent_priority', table_name='complaints')
    op.drop_index('idx_complaints_location', table_name='complaints')
    op.drop_index('idx_complaints_api_list', table_name='complaints')
    op.drop_index('idx_complaints_analytics', table_name='complaints')
    
    # Users table indexes
    op.drop_index('idx_users_phone_unique', table_name='users')
    op.drop_index('idx_users_email_unique', table_name='users')
    op.drop_index('idx_users_constituency_role', table_name='users')
    op.drop_index('idx_users_active_verified', table_name='users')
    
    # Departments table indexes
    op.drop_index('idx_departments_constituency_active', table_name='departments')
    
    # Wards table indexes
    op.drop_index('idx_wards_constituency_number', table_name='wards')
    
    # Status logs indexes
    op.drop_index('idx_status_logs_complaint_timestamp', table_name='status_logs')
    op.drop_index('idx_status_logs_changed_by_timestamp', table_name='status_logs')
    
    # Media table indexes
    op.drop_index('idx_media_complaint_type', table_name='media')
    op.drop_index('idx_media_uploaded_at', table_name='media')
    
    # Constituency indexes
    op.drop_index('idx_constituencies_active', table_name='constituencies')
