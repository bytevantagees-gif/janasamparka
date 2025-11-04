"""add citizen rating and feedback

Revision ID: 006_add_citizen_rating
Revises: 
Create Date: 2025-10-28

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '006_add_citizen_rating'
down_revision = None  # Update this to your latest migration
branch_labels = None
depends_on = None


def upgrade():
    """Add citizen rating and feedback columns to complaints table"""
    op.add_column('complaints', sa.Column('citizen_rating', sa.Integer(), nullable=True))
    op.add_column('complaints', sa.Column('citizen_feedback', sa.Text(), nullable=True))
    op.add_column('complaints', sa.Column('rating_submitted_at', sa.DateTime(), nullable=True))


def downgrade():
    """Remove citizen rating and feedback columns"""
    op.drop_column('complaints', 'rating_submitted_at')
    op.drop_column('complaints', 'citizen_feedback')
    op.drop_column('complaints', 'citizen_rating')
