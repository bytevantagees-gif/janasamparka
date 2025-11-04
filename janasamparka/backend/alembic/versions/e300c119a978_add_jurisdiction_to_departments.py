"""add_jurisdiction_to_departments

Revision ID: e300c119a978
Revises: 79bec4cadb9f
Create Date: 2025-10-30 13:15:08.102639

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e300c119a978'
down_revision = '79bec4cadb9f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add jurisdiction fields to departments table
    # These fields define which panchayat/corporation level the department serves
    # Example: Puttur PWD has taluk_panchayat_id = Puttur TP
    #          Mangalore PWD has city_corporation_id = Mangalore Corporation
    
    op.add_column('departments', sa.Column('gram_panchayat_id', sa.UUID(), nullable=True))
    op.add_column('departments', sa.Column('taluk_panchayat_id', sa.UUID(), nullable=True))
    op.add_column('departments', sa.Column('zilla_panchayat_id', sa.UUID(), nullable=True))
    op.add_column('departments', sa.Column('city_corporation_id', sa.UUID(), nullable=True))
    
    # Create foreign keys
    op.create_foreign_key(
        'fk_departments_gram_panchayat',
        'departments', 'gram_panchayats',
        ['gram_panchayat_id'], ['id'],
        ondelete='CASCADE'
    )
    op.create_foreign_key(
        'fk_departments_taluk_panchayat',
        'departments', 'taluk_panchayats',
        ['taluk_panchayat_id'], ['id'],
        ondelete='CASCADE'
    )
    op.create_foreign_key(
        'fk_departments_zilla_panchayat',
        'departments', 'zilla_panchayats',
        ['zilla_panchayat_id'], ['id'],
        ondelete='CASCADE'
    )
    # Note: city_corporation FK will be added when city_corporations table is created
    
    # Create indexes for jurisdiction filtering
    op.create_index('ix_departments_gram_panchayat_id', 'departments', ['gram_panchayat_id'])
    op.create_index('ix_departments_taluk_panchayat_id', 'departments', ['taluk_panchayat_id'])
    op.create_index('ix_departments_zilla_panchayat_id', 'departments', ['zilla_panchayat_id'])
    op.create_index('ix_departments_city_corporation_id', 'departments', ['city_corporation_id'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_departments_city_corporation_id', table_name='departments')
    op.drop_index('ix_departments_zilla_panchayat_id', table_name='departments')
    op.drop_index('ix_departments_taluk_panchayat_id', table_name='departments')
    op.drop_index('ix_departments_gram_panchayat_id', table_name='departments')
    
    # Drop foreign keys
    op.drop_constraint('fk_departments_zilla_panchayat', 'departments', type_='foreignkey')
    op.drop_constraint('fk_departments_taluk_panchayat', 'departments', type_='foreignkey')
    op.drop_constraint('fk_departments_gram_panchayat', 'departments', type_='foreignkey')
    
    # Drop columns
    op.drop_column('departments', 'city_corporation_id')
    op.drop_column('departments', 'zilla_panchayat_id')
    op.drop_column('departments', 'taluk_panchayat_id')
    op.drop_column('departments', 'gram_panchayat_id')
