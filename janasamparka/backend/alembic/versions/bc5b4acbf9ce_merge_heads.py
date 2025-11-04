"""merge_heads

Revision ID: bc5b4acbf9ce
Revises: add_votebank_engagement_models, e300c119a978
Create Date: 2025-11-01 12:58:21.074999

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bc5b4acbf9ce'
down_revision = ('add_votebank_engagement_models', 'e300c119a978')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
