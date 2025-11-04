"""merge_heads

Revision ID: e2d2ece7df96
Revises: 009_add_backup_login, eea1551a83eb
Create Date: 2025-10-30 15:01:05.753424

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e2d2ece7df96'
down_revision = ('009_add_backup_login', 'eea1551a83eb')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
