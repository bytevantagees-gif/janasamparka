"""ward_panchayat_linking_and_complaint_redesign

Revision ID: 79bec4cadb9f
Revises: a40f314d2bcd
Create Date: 2025-10-30 12:58:51.692089

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = '79bec4cadb9f'
down_revision = 'a40f314d2bcd'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Add ward type and panchayat linking to wards table
    op.add_column('wards', sa.Column('ward_type', sa.String(20), nullable=True))
    op.add_column('wards', sa.Column('gram_panchayat_id', UUID(as_uuid=True), nullable=True))
    op.add_column('wards', sa.Column('taluk_panchayat_id', UUID(as_uuid=True), nullable=True))
    op.add_column('wards', sa.Column('city_corporation_id', UUID(as_uuid=True), nullable=True))
    
    # Create foreign keys for ward-panchayat linking
    op.create_foreign_key(
        'fk_wards_gram_panchayat_id',
        'wards', 'gram_panchayats',
        ['gram_panchayat_id'], ['id']
    )
    op.create_foreign_key(
        'fk_wards_taluk_panchayat_id',
        'wards', 'taluk_panchayats',
        ['taluk_panchayat_id'], ['id']
    )
    
    # Create indexes
    op.create_index('ix_wards_ward_type', 'wards', ['ward_type'])
    op.create_index('ix_wards_gram_panchayat_id', 'wards', ['gram_panchayat_id'])
    op.create_index('ix_wards_taluk_panchayat_id', 'wards', ['taluk_panchayat_id'])
    
    # 2. Add public_notes to complaints table (internal_notes already exists)
    op.add_column('complaints', sa.Column('public_notes', sa.Text, nullable=True))
    
    # 3. Remove direct panchayat assignments from complaints (keep for reference but don't use in new flow)
    # We'll keep the columns but change the routing logic
    # assignment_type will now be: 'ward' or 'department' only
    
    # 4. Add ward_officer_id to track which ward officer is handling the complaint
    op.add_column('complaints', sa.Column('ward_officer_id', UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(
        'fk_complaints_ward_officer_id',
        'complaints', 'users',
        ['ward_officer_id'], ['id']
    )
    op.create_index('ix_complaints_ward_officer_id', 'complaints', ['ward_officer_id'])
    
    # 5. Add new user role for ward officers
    # This will be handled in the UserRole enum - no migration needed for enum
    
    # 6. Add ward_id to users table for ward officer assignment
    op.add_column('users', sa.Column('ward_id', UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(
        'fk_users_ward_id',
        'users', 'wards',
        ['ward_id'], ['id']
    )
    op.create_index('ix_users_ward_id', 'users', ['ward_id'])


def downgrade() -> None:
    # Drop indexes and constraints in reverse order
    op.drop_index('ix_users_ward_id', 'users')
    op.drop_constraint('fk_users_ward_id', 'users', type_='foreignkey')
    op.drop_column('users', 'ward_id')
    
    op.drop_index('ix_complaints_ward_officer_id', 'complaints')
    op.drop_constraint('fk_complaints_ward_officer_id', 'complaints', type_='foreignkey')
    op.drop_column('complaints', 'ward_officer_id')
    op.drop_column('complaints', 'public_notes')
    
    op.drop_index('ix_wards_taluk_panchayat_id', 'wards')
    op.drop_index('ix_wards_gram_panchayat_id', 'wards')
    op.drop_index('ix_wards_ward_type', 'wards')
    
    op.drop_constraint('fk_wards_taluk_panchayat_id', 'wards', type_='foreignkey')
    op.drop_constraint('fk_wards_gram_panchayat_id', 'wards', type_='foreignkey')
    
    op.drop_column('wards', 'city_corporation_id')
    op.drop_column('wards', 'taluk_panchayat_id')
    op.drop_column('wards', 'gram_panchayat_id')
    op.drop_column('wards', 'ward_type')
