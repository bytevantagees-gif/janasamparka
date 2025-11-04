"""merge votebank engagement with is_verified

Revision ID: 8342af30e654
Revises: ab6f39e860c9, bc5b4acbf9ce
Create Date: 2025-11-01 13:38:50.753552

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8342af30e654'
down_revision = ('ab6f39e860c9', 'bc5b4acbf9ce')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
