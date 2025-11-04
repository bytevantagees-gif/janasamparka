"""add_is_verified_to_users

Revision ID: ab6f39e860c9
Revises: e300c119a978
Create Date: 2025-11-01 13:33:34.737638

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'ab6f39e860c9'
down_revision = 'e300c119a978'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add is_verified column to users table
    op.add_column('users', sa.Column('is_verified', sa.Boolean(), nullable=True, default=True))


def downgrade() -> None:
    # Remove is_verified column from users table
    op.drop_column('users', 'is_verified')
