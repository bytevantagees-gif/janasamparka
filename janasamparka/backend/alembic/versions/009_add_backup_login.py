"""add backup login with temporary access codes

Revision ID: 009_add_backup_login
Revises: 008_add_internal_notes
Create Date: 2025-10-30

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '009_add_backup_login'
down_revision = '008_add_internal_notes'
branch_labels = None
depends_on = None


def upgrade():
    """Create temporary_access table and add email to users"""
    # Add email field to users table
    op.add_column('users', sa.Column('email', sa.String(length=255), nullable=True, comment='Email address for backup login'))
    op.create_unique_constraint('uq_users_email', 'users', ['email'])
    op.create_index('ix_users_email', 'users', ['email'])
    
    # Create temporary_access table
    op.create_table(
        'temporary_access',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('access_code', sa.String(6), nullable=False, comment='6-digit access code'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('expires_at', sa.DateTime(), nullable=False, comment='Code expires 24 hours after creation'),
        sa.Column('used_at', sa.DateTime(), nullable=True, comment='When the code was used for login'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
    
    # Create indexes for faster queries
    op.create_index('ix_temporary_access_user_id', 'temporary_access', ['user_id'])
    op.create_index('ix_temporary_access_access_code', 'temporary_access', ['access_code'])
    op.create_index('ix_temporary_access_expires_at', 'temporary_access', ['expires_at'])
    op.create_index('ix_temporary_access_used_at', 'temporary_access', ['used_at'])
    
    # Create unique constraint on access_code to prevent duplicates
    op.create_unique_constraint('uq_temporary_access_code', 'temporary_access', ['access_code'])


def downgrade():
    """Drop temporary_access table and remove email from users"""
    # Drop temporary_access table and its indexes
    op.drop_constraint('uq_temporary_access_code', 'temporary_access', type_='unique')
    op.drop_index('ix_temporary_access_used_at', table_name='temporary_access')
    op.drop_index('ix_temporary_access_expires_at', table_name='temporary_access')
    op.drop_index('ix_temporary_access_access_code', table_name='temporary_access')
    op.drop_index('ix_temporary_access_user_id', table_name='temporary_access')
    op.drop_table('temporary_access')
    
    # Remove email from users
    op.drop_index('ix_users_email', table_name='users')
    op.drop_constraint('uq_users_email', 'users', type_='unique')
    op.drop_column('users', 'email')
