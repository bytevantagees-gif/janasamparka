"""create_missing_citizen_engagement_tables

Revision ID: 1f576ec7b986
Revises: 8342af30e654
Create Date: 2025-11-01 20:23:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '1f576ec7b986'
down_revision = '8342af30e654'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create citizen engagement tables"""
    
    # Create citizen_feedback table
    op.create_table('citizen_feedback',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=sa.text('gen_random_uuid()')),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('feedback_type', sa.Enum('COMPLAINT', 'SUGGESTION', 'IDEA', 'APPRECIATION', 'QUERY', 'GRIEVANCE', 'REQUEST', name='feedbacktype'), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'UNDER_REVIEW', 'IN_PROGRESS', 'RESOLVED', 'REJECTED', 'CLOSED', name='feedbackstatus'), nullable=True),
        sa.Column('priority', sa.Enum('LOW', 'MEDIUM', 'HIGH', 'URGENT', name='feedbackpriority'), nullable=True),
        sa.Column('citizen_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('constituency_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('assigned_to', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('department_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('ward_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('subcategory', sa.String(length=100), nullable=True),
        sa.Column('tags', sa.Text(), nullable=True),
        sa.Column('location_address', sa.Text(), nullable=True),
        sa.Column('latitude', sa.String(length=50), nullable=True),
        sa.Column('longitude', sa.String(length=50), nullable=True),
        sa.Column('attachment_urls', sa.Text(), nullable=True),
        sa.Column('video_url', sa.String(length=500), nullable=True),
        sa.Column('upvotes', sa.Integer(), nullable=True),
        sa.Column('downvotes', sa.Integer(), nullable=True),
        sa.Column('vote_count', sa.Integer(), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=True),
        sa.Column('is_anonymous', sa.Boolean(), nullable=True),
        sa.Column('response_required', sa.Boolean(), nullable=True),
        sa.Column('response_deadline', sa.DateTime(), nullable=True),
        sa.Column('last_response_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('source', sa.String(length=50), nullable=True),
        sa.Column('reference_number', sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(['assigned_to'], ['users.id'], ),
        sa.ForeignKeyConstraint(['citizen_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['constituency_id'], ['constituencies.id'], ),
        sa.ForeignKeyConstraint(['department_id'], ['departments.id'], ),
        sa.ForeignKeyConstraint(['ward_id'], ['wards.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_citizen_feedback_category'), 'citizen_feedback', ['category'], unique=False)
    op.create_index(op.f('ix_citizen_feedback_constituency_id'), 'citizen_feedback', ['constituency_id'], unique=False)
    op.create_index(op.f('ix_citizen_feedback_created_at'), 'citizen_feedback', ['created_at'], unique=False)
    op.create_index(op.f('ix_citizen_feedback_feedback_type'), 'citizen_feedback', ['feedback_type'], unique=False)
    op.create_index(op.f('ix_citizen_feedback_id'), 'citizen_feedback', ['id'], unique=True)
    op.create_index(op.f('ix_citizen_feedback_is_public'), 'citizen_feedback', ['is_public'], unique=False)
    op.create_index(op.f('ix_citizen_feedback_priority'), 'citizen_feedback', ['priority'], unique=False)
    op.create_index(op.f('ix_citizen_feedback_reference_number'), 'citizen_feedback', ['reference_number'], unique=True)
    op.create_index(op.f('ix_citizen_feedback_status'), 'citizen_feedback', ['status'], unique=False)
    op.create_index(op.f('ix_citizen_feedback_subcategory'), 'citizen_feedback', ['subcategory'], unique=False)
    op.create_index(op.f('ix_citizen_feedback_assigned_to'), 'citizen_feedback', ['assigned_to'], unique=False)
    
    # Create feedback_responses table
    op.create_table('feedback_responses',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=sa.text('gen_random_uuid()')),
        sa.Column('feedback_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('response_type', sa.String(length=50), nullable=True),
        sa.Column('responder_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('responder_name', sa.String(length=200), nullable=True),
        sa.Column('responder_role', sa.String(length=50), nullable=True),
        sa.Column('attachment_urls', sa.Text(), nullable=True),
        sa.Column('video_url', sa.String(length=500), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=True),
        sa.Column('is_internal_note', sa.Boolean(), nullable=True),
        sa.Column('status_change', sa.String(length=50), nullable=True),
        sa.Column('old_status', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['feedback_id'], ['citizen_feedback.id'], ),
        sa.ForeignKeyConstraint(['responder_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_feedback_responses_created_at'), 'feedback_responses', ['created_at'], unique=False)
    op.create_index(op.f('ix_feedback_responses_feedback_id'), 'feedback_responses', ['feedback_id'], unique=False)
    op.create_index(op.f('ix_feedback_responses_id'), 'feedback_responses', ['id'], unique=True)
    op.create_index(op.f('ix_feedback_responses_responder_id'), 'feedback_responses', ['responder_id'], unique=False)
    
    # Create feedback_votes table
    op.create_table('feedback_votes',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=sa.text('gen_random_uuid()')),
        sa.Column('feedback_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('voter_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('vote_type', sa.String(length=10), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['feedback_id'], ['citizen_feedback.id'], ),
        sa.ForeignKeyConstraint(['voter_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_feedback_votes_created_at'), 'feedback_votes', ['created_at'], unique=False)
    op.create_index(op.f('ix_feedback_votes_feedback_id'), 'feedback_votes', ['feedback_id'], unique=False)
    op.create_index(op.f('ix_feedback_votes_id'), 'feedback_votes', ['id'], unique=True)
    op.create_index(op.f('ix_feedback_votes_voter_id'), 'feedback_votes', ['voter_id'], unique=False)
    
    # Create video_conferences table
    op.create_table('video_conferences',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=sa.text('gen_random_uuid()')),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('conference_type', sa.Enum('ONE_ON_ONE', 'GROUP_MEETING', 'PUBLIC_HEARING', 'PRESS_CONFERENCE', 'TOWN_HALL', 'OFFICE_HOURS', 'OTHER', name='videoconferencetype'), nullable=False),
        sa.Column('status', sa.Enum('SCHEDULED', 'STARTED', 'ENDED', 'CANCELLED', name='videoconferencestatus'), nullable=True),
        sa.Column('host_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('constituency_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('scheduled_start', sa.DateTime(), nullable=False),
        sa.Column('scheduled_end', sa.DateTime(), nullable=False),
        sa.Column('actual_start', sa.DateTime(), nullable=True),
        sa.Column('actual_end', sa.DateTime(), nullable=True),
        sa.Column('max_participants', sa.Integer(), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=True),
        sa.Column('requires_registration', sa.Boolean(), nullable=True),
        sa.Column('is_recorded', sa.Boolean(), nullable=True),
        sa.Column('platform', sa.String(length=50), nullable=True),
        sa.Column('meeting_id', sa.String(length=100), nullable=True),
        sa.Column('meeting_url', sa.String(length=500), nullable=True),
        sa.Column('meeting_password', sa.String(length=50), nullable=True),
        sa.Column('host_url', sa.String(length=500), nullable=True),
        sa.Column('venue', sa.String(length=500), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('latitude', sa.String(length=50), nullable=True),
        sa.Column('longitude', sa.String(length=50), nullable=True),
        sa.Column('registered_participants', sa.Integer(), nullable=True),
        sa.Column('actual_participants', sa.Integer(), nullable=True),
        sa.Column('recording_url', sa.String(length=500), nullable=True),
        sa.Column('transcript_url', sa.String(length=500), nullable=True),
        sa.Column('attachment_urls', sa.Text(), nullable=True),
        sa.Column('allowed_roles', sa.Text(), nullable=True),
        sa.Column('invite_only', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['constituency_id'], ['constituencies.id'], ),
        sa.ForeignKeyConstraint(['host_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_video_conferences_constituency_id'), 'video_conferences', ['constituency_id'], unique=False)
    op.create_index(op.f('ix_video_conferences_created_at'), 'video_conferences', ['created_at'], unique=False)
    op.create_index(op.f('ix_video_conferences_host_id'), 'video_conferences', ['host_id'], unique=False)
    op.create_index(op.f('ix_video_conferences_id'), 'video_conferences', ['id'], unique=True)
    op.create_index(op.f('ix_video_conferences_is_public'), 'video_conferences', ['is_public'], unique=False)
    op.create_index(op.f('ix_video_conferences_meeting_id'), 'video_conferences', ['meeting_id'], unique=True)
    op.create_index(op.f('ix_video_conferences_scheduled_end'), 'video_conferences', ['scheduled_end'], unique=False)
    op.create_index(op.f('ix_video_conferences_scheduled_start'), 'video_conferences', ['scheduled_start'], unique=False)
    op.create_index(op.f('ix_video_conferences_status'), 'video_conferences', ['status'], unique=False)
    op.create_index(op.f('ix_video_conferences_conference_type'), 'video_conferences', ['conference_type'], unique=False)
    
    # Create conference_participants table
    op.create_table('conference_participants',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=sa.text('gen_random_uuid()')),
        sa.Column('conference_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('participant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('registered_at', sa.DateTime(), nullable=True),
        sa.Column('joined_at', sa.DateTime(), nullable=True),
        sa.Column('left_at', sa.DateTime(), nullable=True),
        sa.Column('role', sa.String(length=50), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('email', sa.String(length=200), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['conference_id'], ['video_conferences.id'], ),
        sa.ForeignKeyConstraint(['participant_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_conference_participants_conference_id'), 'conference_participants', ['conference_id'], unique=False)
    op.create_index(op.f('ix_conference_participants_id'), 'conference_participants', ['id'], unique=True)
    op.create_index(op.f('ix_conference_participants_participant_id'), 'conference_participants', ['participant_id'], unique=False)
    
    # Create scheduled_broadcasts table
    op.create_table('scheduled_broadcasts',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=sa.text('gen_random_uuid()')),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('broadcast_type', sa.Enum('ANNOUNCEMENT', 'EMERGENCY', 'UPDATE', 'INVITATION', 'REMINDER', 'CELEBRATION', 'INFORMATION', name='broadcasttype'), nullable=False),
        sa.Column('status', sa.Enum('DRAFT', 'SCHEDULED', 'SENT', 'FAILED', 'CANCELLED', name='broadcaststatus'), nullable=True),
        sa.Column('sender_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('constituency_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('scheduled_at', sa.DateTime(), nullable=False),
        sa.Column('sent_at', sa.DateTime(), nullable=True),
        sa.Column('target_roles', sa.Text(), nullable=True),
        sa.Column('target_wards', sa.Text(), nullable=True),
        sa.Column('target_departments', sa.Text(), nullable=True),
        sa.Column('target_all', sa.Boolean(), nullable=True),
        sa.Column('send_push', sa.Boolean(), nullable=True),
        sa.Column('send_sms', sa.Boolean(), nullable=True),
        sa.Column('send_email', sa.Boolean(), nullable=True),
        sa.Column('send_whatsapp', sa.Boolean(), nullable=True),
        sa.Column('show_in_app', sa.Boolean(), nullable=True),
        sa.Column('attachment_urls', sa.Text(), nullable=True),
        sa.Column('video_url', sa.String(length=500), nullable=True),
        sa.Column('link_url', sa.String(length=500), nullable=True),
        sa.Column('link_text', sa.String(length=200), nullable=True),
        sa.Column('priority', sa.Integer(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('requires_approval', sa.Boolean(), nullable=True),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('sent_count', sa.Integer(), nullable=True),
        sa.Column('delivered_count', sa.Integer(), nullable=True),
        sa.Column('read_count', sa.Integer(), nullable=True),
        sa.Column('click_count', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['approved_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['constituency_id'], ['constituencies.id'], ),
        sa.ForeignKeyConstraint(['sender_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_scheduled_broadcasts_constituency_id'), 'scheduled_broadcasts', ['constituency_id'], unique=False)
    op.create_index(op.f('ix_scheduled_broadcasts_created_at'), 'scheduled_broadcasts', ['created_at'], unique=False)
    op.create_index(op.f('ix_scheduled_broadcasts_id'), 'scheduled_broadcasts', ['id'], unique=True)
    op.create_index(op.f('ix_scheduled_broadcasts_scheduled_at'), 'scheduled_broadcasts', ['scheduled_at'], unique=False)
    op.create_index(op.f('ix_scheduled_broadcasts_sender_id'), 'scheduled_broadcasts', ['sender_id'], unique=False)
    op.create_index(op.f('ix_scheduled_broadcasts_status'), 'scheduled_broadcasts', ['status'], unique=False)
    
    # Create broadcast_deliveries table
    op.create_table('broadcast_deliveries',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=sa.text('gen_random_uuid()')),
        sa.Column('broadcast_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('push_sent', sa.Boolean(), nullable=True),
        sa.Column('push_delivered', sa.Boolean(), nullable=True),
        sa.Column('push_read', sa.Boolean(), nullable=True),
        sa.Column('sms_sent', sa.Boolean(), nullable=True),
        sa.Column('sms_delivered', sa.Boolean(), nullable=True),
        sa.Column('email_sent', sa.Boolean(), nullable=True),
        sa.Column('email_delivered', sa.Boolean(), nullable=True),
        sa.Column('email_read', sa.Boolean(), nullable=True),
        sa.Column('whatsapp_sent', sa.Boolean(), nullable=True),
        sa.Column('whatsapp_delivered', sa.Boolean(), nullable=True),
        sa.Column('whatsapp_read', sa.Boolean(), nullable=True),
        sa.Column('shown_in_app', sa.Boolean(), nullable=True),
        sa.Column('clicked_in_app', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['broadcast_id'], ['scheduled_broadcasts.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_broadcast_deliveries_broadcast_id'), 'broadcast_deliveries', ['broadcast_id'], unique=False)
    op.create_index(op.f('ix_broadcast_deliveries_id'), 'broadcast_deliveries', ['id'], unique=True)
    op.create_index(op.f('ix_broadcast_deliveries_user_id'), 'broadcast_deliveries', ['user_id'], unique=False)


def downgrade() -> None:
    """Drop citizen engagement tables"""
    
    # Drop broadcast_deliveries table
    op.drop_index(op.f('ix_broadcast_deliveries_user_id'), table_name='broadcast_deliveries')
    op.drop_index(op.f('ix_broadcast_deliveries_id'), table_name='broadcast_deliveries')
    op.drop_index(op.f('ix_broadcast_deliveries_broadcast_id'), table_name='broadcast_deliveries')
    op.drop_table('broadcast_deliveries')
    
    # Drop scheduled_broadcasts table
    op.drop_index(op.f('ix_scheduled_broadcasts_status'), table_name='scheduled_broadcasts')
    op.drop_index(op.f('ix_scheduled_broadcasts_sender_id'), table_name='scheduled_broadcasts')
    op.drop_index(op.f('ix_scheduled_broadcasts_scheduled_at'), table_name='scheduled_broadcasts')
    op.drop_index(op.f('ix_scheduled_broadcasts_id'), table_name='scheduled_broadcasts')
    op.drop_index(op.f('ix_scheduled_broadcasts_created_at'), table_name='scheduled_broadcasts')
    op.drop_index(op.f('ix_scheduled_broadcasts_constituency_id'), table_name='scheduled_broadcasts')
    op.drop_table('scheduled_broadcasts')
    
    # Drop conference_participants table
    op.drop_index(op.f('ix_conference_participants_participant_id'), table_name='conference_participants')
    op.drop_index(op.f('ix_conference_participants_id'), table_name='conference_participants')
    op.drop_index(op.f('ix_conference_participants_conference_id'), table_name='conference_participants')
    op.drop_table('conference_participants')
    
    # Drop video_conferences table
    op.drop_index(op.f('ix_video_conferences_conference_type'), table_name='video_conferences')
    op.drop_index(op.f('ix_video_conferences_status'), table_name='video_conferences')
    op.drop_index(op.f('ix_video_conferences_scheduled_start'), table_name='video_conferences')
    op.drop_index(op.f('ix_video_conferences_scheduled_end'), table_name='video_conferences')
    op.drop_index(op.f('ix_video_conferences_meeting_id'), table_name='video_conferences')
    op.drop_index(op.f('ix_video_conferences_is_public'), table_name='video_conferences')
    op.drop_index(op.f('ix_video_conferences_id'), table_name='video_conferences')
    op.drop_index(op.f('ix_video_conferences_created_at'), table_name='video_conferences')
    op.drop_index(op.f('ix_video_conferences_host_id'), table_name='video_conferences')
    op.drop_index(op.f('ix_video_conferences_constituency_id'), table_name='video_conferences')
    op.drop_table('video_conferences')
    
    # Drop feedback_votes table
    op.drop_index(op.f('ix_feedback_votes_voter_id'), table_name='feedback_votes')
    op.drop_index(op.f('ix_feedback_votes_id'), table_name='feedback_votes')
    op.drop_index(op.f('ix_feedback_votes_feedback_id'), table_name='feedback_votes')
    op.drop_index(op.f('ix_feedback_votes_created_at'), table_name='feedback_votes')
    op.drop_table('feedback_votes')
    
    # Drop feedback_responses table
    op.drop_index(op.f('ix_feedback_responses_responder_id'), table_name='feedback_responses')
    op.drop_index(op.f('ix_feedback_responses_id'), table_name='feedback_responses')
    op.drop_index(op.f('ix_feedback_responses_feedback_id'), table_name='feedback_responses')
    op.drop_index(op.f('ix_feedback_responses_created_at'), table_name='feedback_responses')
    op.drop_table('feedback_responses')
    
    # Drop citizen_feedback table
    op.drop_index(op.f('ix_citizen_feedback_assigned_to'), table_name='citizen_feedback')
    op.drop_index(op.f('ix_citizen_feedback_subcategory'), table_name='citizen_feedback')
    op.drop_index(op.f('ix_citizen_feedback_status'), table_name='citizen_feedback')
    op.drop_index(op.f('ix_citizen_feedback_reference_number'), table_name='citizen_feedback')
    op.drop_index(op.f('ix_citizen_feedback_priority'), table_name='citizen_feedback')
    op.drop_index(op.f('ix_citizen_feedback_is_public'), table_name='citizen_feedback')
    op.drop_index(op.f('ix_citizen_feedback_id'), table_name='citizen_feedback')
    op.drop_index(op.f('ix_citizen_feedback_feedback_type'), table_name='citizen_feedback')
    op.drop_index(op.f('ix_citizen_feedback_created_at'), table_name='citizen_feedback')
    op.drop_index(op.f('ix_citizen_feedback_constituency_id'), table_name='citizen_feedback')
    op.drop_index(op.f('ix_citizen_feedback_category'), table_name='citizen_feedback')
    op.drop_table('citizen_feedback')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS feedbacktype')
    op.execute('DROP TYPE IF EXISTS feedbackstatus')
    op.execute('DROP TYPE IF EXISTS feedbackpriority')
    op.execute('DROP TYPE IF EXISTS videoconferencetype')
    op.execute('DROP TYPE IF EXISTS videoconferencestatus')
    op.execute('DROP TYPE IF EXISTS broadcasttype')
    op.execute('DROP TYPE IF EXISTS broadcaststatus')
