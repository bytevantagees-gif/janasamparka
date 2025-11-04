"""Add work approval columns to complaints

Revision ID: 002_work_approval
Revises: 001_multi_tenant
Create Date: 2025-10-28 17:20:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002_work_approval'
down_revision = '001_multi_tenant'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add work approval columns to complaints table
    op.add_column('complaints', sa.Column('work_approved', sa.Boolean, nullable=True))
    op.add_column('complaints', sa.Column('approval_comments', sa.Text, nullable=True))
    op.add_column('complaints', sa.Column('approved_at', sa.DateTime, nullable=True))
    op.add_column('complaints', sa.Column('approved_by', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('complaints', sa.Column('rejection_reason', sa.Text, nullable=True))
    op.add_column('complaints', sa.Column('rejected_at', sa.DateTime, nullable=True))
    op.add_column('complaints', sa.Column('rejected_by', postgresql.UUID(as_uuid=True), nullable=True))
    
    # Add foreign key constraints
    op.create_foreign_key(
        'fk_complaints_approved_by',
        'complaints', 'users',
        ['approved_by'], ['id']
    )
    op.create_foreign_key(
        'fk_complaints_rejected_by',
        'complaints', 'users',
        ['rejected_by'], ['id']
    )
    
    # Add missing columns to media table (photo_type, caption)
    op.add_column('media', sa.Column('photo_type', sa.String(20), nullable=True))
    op.add_column('media', sa.Column('caption', sa.Text, nullable=True))


def downgrade() -> None:
    # Drop columns from media table
    op.drop_column('media', 'caption')
    op.drop_column('media', 'photo_type')
    
    # Drop foreign key constraints
    op.drop_constraint('fk_complaints_rejected_by', 'complaints', type_='foreignkey')
    op.drop_constraint('fk_complaints_approved_by', 'complaints', type_='foreignkey')
    
    # Drop columns from complaints table
    op.drop_column('complaints', 'rejected_by')
    op.drop_column('complaints', 'rejected_at')
    op.drop_column('complaints', 'rejection_reason')
    op.drop_column('complaints', 'approved_by')
    op.drop_column('complaints', 'approved_at')
    op.drop_column('complaints', 'approval_comments')
    op.drop_column('complaints', 'work_approved')
