"""add internal notes to complaints

Revision ID: 008_add_internal_notes
Revises: 007_add_satisfaction_interventions
Create Date: 2025-10-30

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '008_add_internal_notes'
down_revision = '007_add_satisfaction_interventions'
branch_labels = None
depends_on = None


def upgrade():
    """Add internal notes columns to complaints table"""
    op.add_column('complaints', sa.Column('internal_notes', sa.Text(), nullable=True, comment='Internal notes visible only to officials'))
    op.add_column('complaints', sa.Column('notes_are_internal', sa.Boolean(), nullable=False, server_default='true', comment='Whether notes are internal (true) or public (false)'))
    op.add_column('complaints', sa.Column('notes_updated_at', sa.DateTime(), nullable=True, comment='When notes were last updated'))
    op.add_column('complaints', sa.Column('notes_updated_by', sa.String(length=255), nullable=True, comment='User ID who last updated notes'))


def downgrade():
    """Remove internal notes columns"""
    op.drop_column('complaints', 'notes_updated_by')
    op.drop_column('complaints', 'notes_updated_at')
    op.drop_column('complaints', 'notes_are_internal')
    op.drop_column('complaints', 'internal_notes')
