"""add satisfaction interventions table

Revision ID: 007_add_satisfaction_interventions
Revises: 006_add_citizen_rating
Create Date: 2025-01-XX

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '007_add_satisfaction_interventions'
down_revision = '006_add_citizen_rating'
branch_labels = None
depends_on = None


def upgrade():
    """Create satisfaction_interventions table for tracking moderator interventions with unhappy citizens"""
    op.create_table(
        'satisfaction_interventions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('complaint_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('citizen_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('moderator_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('intervention_type', sa.String(50), nullable=False, comment='Type of intervention: call, visit, follow-up'),
        sa.Column('notes', sa.Text(), nullable=True, comment='Moderator notes about the intervention plan'),
        sa.Column('scheduled_at', sa.DateTime(), nullable=True, comment='When the intervention is scheduled'),
        sa.Column('completed_at', sa.DateTime(), nullable=True, comment='When the intervention was completed'),
        sa.Column('outcome', sa.String(50), nullable=True, comment='Outcome: resolved, escalated, pending'),
        sa.Column('completion_notes', sa.Text(), nullable=True, comment='Notes after completing the intervention'),
        sa.Column('citizen_now_happy', sa.Boolean(), nullable=True, comment='Whether citizen is satisfied after intervention'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()'), onupdate=sa.text('now()')),
        sa.ForeignKeyConstraint(['complaint_id'], ['complaints.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['citizen_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['moderator_id'], ['users.id'], ondelete='SET NULL')
    )
    
    # Create indexes for faster queries
    op.create_index('ix_satisfaction_interventions_complaint_id', 'satisfaction_interventions', ['complaint_id'])
    op.create_index('ix_satisfaction_interventions_citizen_id', 'satisfaction_interventions', ['citizen_id'])
    op.create_index('ix_satisfaction_interventions_moderator_id', 'satisfaction_interventions', ['moderator_id'])
    op.create_index('ix_satisfaction_interventions_scheduled_at', 'satisfaction_interventions', ['scheduled_at'])
    op.create_index('ix_satisfaction_interventions_completed_at', 'satisfaction_interventions', ['completed_at'])
    op.create_index('ix_satisfaction_interventions_outcome', 'satisfaction_interventions', ['outcome'])


def downgrade():
    """Drop satisfaction_interventions table and its indexes"""
    op.drop_index('ix_satisfaction_interventions_outcome', table_name='satisfaction_interventions')
    op.drop_index('ix_satisfaction_interventions_completed_at', table_name='satisfaction_interventions')
    op.drop_index('ix_satisfaction_interventions_scheduled_at', table_name='satisfaction_interventions')
    op.drop_index('ix_satisfaction_interventions_moderator_id', table_name='satisfaction_interventions')
    op.drop_index('ix_satisfaction_interventions_citizen_id', table_name='satisfaction_interventions')
    op.drop_index('ix_satisfaction_interventions_complaint_id', table_name='satisfaction_interventions')
    op.drop_table('satisfaction_interventions')
