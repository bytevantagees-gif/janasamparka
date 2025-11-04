"""Add budget tracking and FAQ tables

Revision ID: c0fc432d3f05
Revises: add_case_notes_routing
Create Date: 2025-10-30 09:58:45.938871

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'c0fc432d3f05'
down_revision = 'add_case_notes_routing'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create TransactionType enum
    transaction_type_enum = postgresql.ENUM(
        'allocation', 'commitment', 'expense', 'refund',
        name='transactiontype',
        create_type=False
    )
    transaction_type_enum.create(op.get_bind(), checkfirst=True)
    
    # Create ward_budgets table
    op.create_table(
        'ward_budgets',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('ward_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('wards.id'), nullable=False, index=True),
        sa.Column('financial_year', sa.String(10), nullable=False),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('allocated', sa.Integer(), nullable=False, comment='Amount in rupees'),
        sa.Column('spent', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('committed', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_ward_budgets_financial_year', 'ward_budgets', ['financial_year'])
    op.create_index('ix_ward_budgets_category', 'ward_budgets', ['category'])
    
    # Create department_budgets table
    op.create_table(
        'department_budgets',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('department_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('departments.id'), nullable=False, index=True),
        sa.Column('constituency_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('constituencies.id'), nullable=False, index=True),
        sa.Column('financial_year', sa.String(10), nullable=False),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('allocated', sa.Integer(), nullable=False),
        sa.Column('spent', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('committed', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_department_budgets_financial_year', 'department_budgets', ['financial_year'])
    op.create_index('ix_department_budgets_category', 'department_budgets', ['category'])
    
    # Create budget_transactions table
    op.create_table(
        'budget_transactions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('ward_budget_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('ward_budgets.id'), nullable=True, index=True),
        sa.Column('department_budget_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('department_budgets.id'), nullable=True, index=True),
        sa.Column('transaction_type', transaction_type_enum, nullable=False),
        sa.Column('amount', sa.Integer(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('complaint_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('complaints.id'), nullable=True, index=True),
        sa.Column('performed_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('performed_at', sa.DateTime(), nullable=False, index=True),
    )
    
    # Create faq_solutions table
    op.create_table(
        'faq_solutions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('constituency_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('constituencies.id'), nullable=True, index=True),
        sa.Column('category', sa.String(50), nullable=False, index=True),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('question_keywords', sa.Text(), nullable=False, comment='Comma-separated keywords for search'),
        sa.Column('solution_text', sa.Text(), nullable=False),
        sa.Column('solution_steps', sa.Text(), nullable=True),
        sa.Column('kannada_title', sa.String(200), nullable=True),
        sa.Column('kannada_solution', sa.Text(), nullable=True),
        sa.Column('view_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('helpful_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('not_helpful_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('prevented_complaints_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, index=True),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    
    # Add new columns to complaints table for priority scoring and duplicate detection
    op.add_column('complaints', sa.Column('priority_score', sa.Numeric(precision=5, scale=2), nullable=True))
    op.add_column('complaints', sa.Column('affected_population_estimate', sa.Integer(), nullable=True))
    op.add_column('complaints', sa.Column('is_emergency', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('complaints', sa.Column('is_duplicate', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('complaints', sa.Column('parent_complaint_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('complaints.id'), nullable=True))
    op.add_column('complaints', sa.Column('duplicate_count', sa.Integer(), nullable=False, server_default='0'))
    
    # Create indexes for new complaint columns
    op.create_index('ix_complaints_priority_score', 'complaints', ['priority_score'])
    op.create_index('ix_complaints_is_emergency', 'complaints', ['is_emergency'])
    op.create_index('ix_complaints_is_duplicate', 'complaints', ['is_duplicate'])
    op.create_index('ix_complaints_parent_complaint_id', 'complaints', ['parent_complaint_id'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_complaints_parent_complaint_id', 'complaints')
    op.drop_index('ix_complaints_is_duplicate', 'complaints')
    op.drop_index('ix_complaints_is_emergency', 'complaints')
    op.drop_index('ix_complaints_priority_score', 'complaints')
    
    # Drop complaint columns
    op.drop_column('complaints', 'duplicate_count')
    op.drop_column('complaints', 'parent_complaint_id')
    op.drop_column('complaints', 'is_duplicate')
    op.drop_column('complaints', 'is_emergency')
    op.drop_column('complaints', 'affected_population_estimate')
    op.drop_column('complaints', 'priority_score')
    
    # Drop tables
    op.drop_table('faq_solutions')
    op.drop_table('budget_transactions')
    op.drop_table('department_budgets')
    op.drop_table('ward_budgets')
    
    # Drop enum
    sa.Enum(name='transactiontype').drop(op.get_bind(), checkfirst=True)
