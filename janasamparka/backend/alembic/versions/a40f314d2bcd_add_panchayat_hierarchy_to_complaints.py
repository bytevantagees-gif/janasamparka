"""add_panchayat_hierarchy_to_complaints

Revision ID: a40f314d2bcd
Revises: e2d2ece7df96
Create Date: 2025-10-30 12:43:24.177144

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = 'a40f314d2bcd'
down_revision = 'e2d2ece7df96'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add taluk_panchayat_id and zilla_panchayat_id to complaints table
    op.add_column('complaints', sa.Column('taluk_panchayat_id', UUID(as_uuid=True), nullable=True))
    op.add_column('complaints', sa.Column('zilla_panchayat_id', UUID(as_uuid=True), nullable=True))
    op.add_column('complaints', sa.Column('assignment_type', sa.String(20), nullable=True))
    
    # Create foreign key constraints
    op.create_foreign_key(
        'fk_complaints_taluk_panchayat_id',
        'complaints', 'taluk_panchayats',
        ['taluk_panchayat_id'], ['id']
    )
    op.create_foreign_key(
        'fk_complaints_zilla_panchayat_id',
        'complaints', 'zilla_panchayats',
        ['zilla_panchayat_id'], ['id']
    )
    
    # Create indexes for better query performance
    op.create_index('ix_complaints_taluk_panchayat_id', 'complaints', ['taluk_panchayat_id'])
    op.create_index('ix_complaints_zilla_panchayat_id', 'complaints', ['zilla_panchayat_id'])
    op.create_index('ix_complaints_assignment_type', 'complaints', ['assignment_type'])
    
    # Add department_id to users table
    op.add_column('users', sa.Column('department_id', UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(
        'fk_users_department_id',
        'users', 'departments',
        ['department_id'], ['id']
    )
    op.create_index('ix_users_department_id', 'users', ['department_id'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_users_department_id', 'users')
    op.drop_index('ix_complaints_assignment_type', 'complaints')
    op.drop_index('ix_complaints_zilla_panchayat_id', 'complaints')
    op.drop_index('ix_complaints_taluk_panchayat_id', 'complaints')
    
    # Drop foreign keys
    op.drop_constraint('fk_users_department_id', 'users', type_='foreignkey')
    op.drop_constraint('fk_complaints_zilla_panchayat_id', 'complaints', type_='foreignkey')
    op.drop_constraint('fk_complaints_taluk_panchayat_id', 'complaints', type_='foreignkey')
    
    # Drop columns
    op.drop_column('users', 'department_id')
    op.drop_column('complaints', 'assignment_type')
    op.drop_column('complaints', 'zilla_panchayat_id')
    op.drop_column('complaints', 'taluk_panchayat_id')

