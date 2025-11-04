"""Add case notes, department routing, and escalations

Revision ID: add_case_notes_routing
Revises: 
Create Date: 2025-10-30 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_case_notes_routing'
down_revision = ('002_work_approval', '006_add_citizen_rating')  # Merge both heads
branch_labels = None
depends_on = None


def upgrade():
    # Add new columns to complaints table
    op.add_column('complaints', sa.Column('suggested_dept_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('complaints', sa.Column('citizen_selected_dept', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('complaints', sa.Column('last_activity_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')))
    
    op.create_foreign_key('fk_complaints_suggested_dept', 'complaints', 'departments', ['suggested_dept_id'], ['id'])
    
    # Create case_notes table
    op.create_table('case_notes',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('complaint_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('note', sa.Text(), nullable=False),
        sa.Column('note_type', sa.String(length=50), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('is_public', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('resets_idle_timer', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['complaint_id'], ['complaints.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_case_notes_complaint_id'), 'case_notes', ['complaint_id'], unique=False)
    op.create_index(op.f('ix_case_notes_created_at'), 'case_notes', ['created_at'], unique=False)
    
    # Create department_routing table
    op.create_table('department_routing',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('complaint_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('from_dept_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('to_dept_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('reason', sa.String(length=50), nullable=False),
        sa.Column('comments', sa.Text(), nullable=True),
        sa.Column('routed_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('routed_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('accepted', sa.Boolean(), nullable=True),
        sa.Column('accepted_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('accepted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['complaint_id'], ['complaints.id'], ),
        sa.ForeignKeyConstraint(['from_dept_id'], ['departments.id'], ),
        sa.ForeignKeyConstraint(['to_dept_id'], ['departments.id'], ),
        sa.ForeignKeyConstraint(['routed_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['accepted_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_department_routing_complaint_id'), 'department_routing', ['complaint_id'], unique=False)
    op.create_index(op.f('ix_department_routing_routed_at'), 'department_routing', ['routed_at'], unique=False)
    
    # Create complaint_escalations table
    op.create_table('complaint_escalations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('complaint_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('reason', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('escalated_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('resolved', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('resolution_notes', sa.Text(), nullable=True),
        sa.Column('resolved_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['complaint_id'], ['complaints.id'], ),
        sa.ForeignKeyConstraint(['escalated_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['resolved_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_complaint_escalations_complaint_id'), 'complaint_escalations', ['complaint_id'], unique=False)
    op.create_index(op.f('ix_complaint_escalations_created_at'), 'complaint_escalations', ['created_at'], unique=False)


def downgrade():
    # Drop tables
    op.drop_index(op.f('ix_complaint_escalations_created_at'), table_name='complaint_escalations')
    op.drop_index(op.f('ix_complaint_escalations_complaint_id'), table_name='complaint_escalations')
    op.drop_table('complaint_escalations')
    
    op.drop_index(op.f('ix_department_routing_routed_at'), table_name='department_routing')
    op.drop_index(op.f('ix_department_routing_complaint_id'), table_name='department_routing')
    op.drop_table('department_routing')
    
    op.drop_index(op.f('ix_case_notes_created_at'), table_name='case_notes')
    op.drop_index(op.f('ix_case_notes_complaint_id'), table_name='case_notes')
    op.drop_table('case_notes')
    
    # Drop columns from complaints table
    op.drop_constraint('fk_complaints_suggested_dept', 'complaints', type_='foreignkey')
    op.drop_column('complaints', 'last_activity_at')
    op.drop_column('complaints', 'citizen_selected_dept')
    op.drop_column('complaints', 'suggested_dept_id')
