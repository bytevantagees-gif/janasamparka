"""Add votebank engagement models

Revision ID: add_votebank_engagement_models
Revises: add_citizen_engagement_models
Create Date: 2024-11-01 18:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_votebank_engagement_models'
down_revision = 'add_citizen_engagement_models'
branch_labels = None
depends_on = None


def upgrade():
    # Create enums for votebank engagement using SQLAlchemy's Enum which handles checkfirst
    # Note: We don't need to create enums explicitly as they will be created with the tables

    # Create farmer_profiles table
    op.create_table('farmer_profiles',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=sa.text('gen_random_uuid()')),
        sa.Column('farmer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('constituency_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('ward_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('land_area_acres', sa.Float(), nullable=True),
        sa.Column('land_area_hectares', sa.Float(), nullable=True),
        sa.Column('soil_type', sa.String(length=100), nullable=True),
        sa.Column('water_source', sa.String(length=100), nullable=True),
        sa.Column('irrigation_type', sa.String(length=100), nullable=True),
        sa.Column('farming_type', sa.Enum('organic', 'conventional', 'natural', 'zero_budget', 'precision', 'greenhouse', 'hydroponic', 'mixed', name='farming_type'), nullable=True),
        sa.Column('primary_crops', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('secondary_crops', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('livestock_count', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('farm_equipment', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('government_schemes', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('mla_support_received', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('insurance_policies', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('farm_address', sa.Text(), nullable=True),
        sa.Column('farm_latitude', sa.String(length=50), nullable=True),
        sa.Column('farm_longitude', sa.String(length=50), nullable=True),
        sa.Column('preferred_language', sa.String(length=50), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('priority_farmer', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('last_visit_date', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['constituency_id'], ['constituencies.id'], ),
        sa.ForeignKeyConstraint(['farmer_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['ward_id'], ['wards.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_farmer_profiles_constituency_id'), 'farmer_profiles', ['constituency_id'], unique=False)
    op.create_index(op.f('ix_farmer_profiles_farmer_id'), 'farmer_profiles', ['farmer_id'], unique=False)
    op.create_index(op.f('ix_farmer_profiles_ward_id'), 'farmer_profiles', ['ward_id'], unique=False)

    # Create crop_requests table
    op.create_table('crop_requests',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('farmer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('constituency_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('crop_type', sa.Enum('food_grains', 'vegetables', 'fruits', 'commercial_crops', 'spices', 'plantation', 'horticulture', 'livestock', 'dairy', 'poultry', 'fishery', 'other', name='crop_type'), nullable=False),
        sa.Column('crop_name', sa.String(length=100), nullable=False),
        sa.Column('variety', sa.String(length=100), nullable=True),
        sa.Column('expected_harvest_date', sa.DateTime(), nullable=True),
        sa.Column('current_market_price', sa.Float(), nullable=True),
        sa.Column('expected_market_price', sa.Float(), nullable=True),
        sa.Column('target_market', sa.String(length=200), nullable=True),
        sa.Column('request_type', sa.String(length=50), nullable=True),
        sa.Column('quantity_available', sa.Float(), nullable=True),
        sa.Column('quality_grade', sa.String(length=50), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('priority', sa.String(length=50), nullable=True),
        sa.Column('buyer_contacts', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('market_suggestions', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('mla_assistance', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['constituency_id'], ['constituencies.id'], ),
        sa.ForeignKeyConstraint(['farmer_id'], ['farmer_profiles.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_crop_requests_constituency_id'), 'crop_requests', ['constituency_id'], unique=False)
    op.create_index(op.f('ix_crop_requests_crop_type'), 'crop_requests', ['crop_type'], unique=False)
    op.create_index(op.f('ix_crop_requests_farmer_id'), 'crop_requests', ['farmer_id'], unique=False)

    # Create market_listings table
    op.create_table('market_listings',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('farmer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('constituency_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('crop_type', sa.Enum('food_grains', 'vegetables', 'fruits', 'commercial_crops', 'spices', 'plantation', 'horticulture', 'livestock', 'dairy', 'poultry', 'fishery', 'other', name='crop_type'), nullable=False),
        sa.Column('product_name', sa.String(length=200), nullable=False),
        sa.Column('variety', sa.String(length=100), nullable=True),
        sa.Column('quantity', sa.Float(), nullable=False),
        sa.Column('unit', sa.String(length=50), nullable=True),
        sa.Column('quality_grade', sa.String(length=50), nullable=True),
        sa.Column('is_organic', sa.Boolean(), nullable=True),
        sa.Column('certification', sa.String(length=200), nullable=True),
        sa.Column('expected_price', sa.Float(), nullable=True),
        sa.Column('minimum_price', sa.Float(), nullable=True),
        sa.Column('price_negotiable', sa.Boolean(), nullable=True),
        sa.Column('farm_location', sa.String(length=500), nullable=True),
        sa.Column('delivery_available', sa.Boolean(), nullable=True),
        sa.Column('delivery_radius_km', sa.Integer(), nullable=True),
        sa.Column('product_photos', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('quality_videos', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('certificates', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('featured_listing', sa.Boolean(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('interested_buyers', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('views_count', sa.Integer(), nullable=True),
        sa.Column('contacts_count', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('sold_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['constituency_id'], ['constituencies.id'], ),
        sa.ForeignKeyConstraint(['farmer_id'], ['farmer_profiles.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_market_listings_constituency_id'), 'market_listings', ['constituency_id'], unique=False)
    op.create_index(op.f('ix_market_listings_crop_type'), 'market_listings', ['crop_type'], unique=False)
    op.create_index(op.f('ix_market_listings_farmer_id'), 'market_listings', ['farmer_id'], unique=False)

    # Create business_profiles table
    op.create_table('business_profiles',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('constituency_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('ward_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('business_name', sa.String(length=200), nullable=False),
        sa.Column('business_category', sa.Enum('retail', 'manufacturing', 'services', 'agriculture', 'technology', 'construction', 'transport', 'tourism', 'education', 'healthcare', 'finance', 'real_estate', 'other', name='business_category'), nullable=False),
        sa.Column('business_size', sa.Enum('micro', 'small', 'medium', 'large', name='business_size'), nullable=True),
        sa.Column('registration_number', sa.String(length=100), nullable=True),
        sa.Column('gst_number', sa.String(length=50), nullable=True),
        sa.Column('license_type', sa.String(length=100), nullable=True),
        sa.Column('license_expiry', sa.DateTime(), nullable=True),
        sa.Column('year_established', sa.Integer(), nullable=True),
        sa.Column('employee_count', sa.Integer(), nullable=True),
        sa.Column('annual_turnover', sa.Float(), nullable=True),
        sa.Column('business_address', sa.Text(), nullable=True),
        sa.Column('business_phone', sa.String(length=20), nullable=True),
        sa.Column('business_email', sa.String(length=200), nullable=True),
        sa.Column('website', sa.String(length=500), nullable=True),
        sa.Column('business_latitude', sa.String(length=50), nullable=True),
        sa.Column('business_longitude', sa.String(length=50), nullable=True),
        sa.Column('mla_support_received', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('government_schemes', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('bank_loans', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('business_associations', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('partnership_interests', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('featured_business', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('last_verification_date', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['constituency_id'], ['constituencies.id'], ),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['ward_id'], ['wards.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_business_profiles_constituency_id'), 'business_profiles', ['constituency_id'], unique=False)
    op.create_index(op.f('ix_business_profiles_owner_id'), 'business_profiles', ['owner_id'], unique=False)
    op.create_index(op.f('ix_business_profiles_ward_id'), 'business_profiles', ['ward_id'], unique=False)

    # Create business_requests table
    op.create_table('business_requests',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('business_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('constituency_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('request_type', sa.String(length=100), nullable=True),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('funding_amount', sa.Float(), nullable=True),
        sa.Column('partnership_type', sa.String(length=100), nullable=True),
        sa.Column('license_type', sa.String(length=100), nullable=True),
        sa.Column('market_expansion', sa.String(length=200), nullable=True),
        sa.Column('urgency_level', sa.String(length=50), nullable=True),
        sa.Column('expected_resolution', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('priority', sa.String(length=50), nullable=True),
        sa.Column('mla_assistance', sa.Text(), nullable=True),
        sa.Column('government_schemes_suggested', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('potential_partners', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('funding_sources', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('documents', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('presentations', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['business_id'], ['business_profiles.id'], ),
        sa.ForeignKeyConstraint(['constituency_id'], ['constituencies.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_business_requests_business_id'), 'business_requests', ['business_id'], unique=False)
    op.create_index(op.f('ix_business_requests_constituency_id'), 'business_requests', ['constituency_id'], unique=False)

    # Create business_connections table
    op.create_table('business_connections',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('business_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('connected_business_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('constituency_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('connection_type', sa.String(length=100), nullable=True),
        sa.Column('collaboration_interest', sa.String(length=200), nullable=True),
        sa.Column('looking_for', sa.String(length=500), nullable=True),
        sa.Column('offering', sa.String(length=500), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('connection_strength', sa.String(length=50), nullable=True),
        sa.Column('last_interaction_date', sa.DateTime(), nullable=True),
        sa.Column('interaction_count', sa.Integer(), nullable=True),
        sa.Column('successful_collaborations', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['business_id'], ['business_profiles.id'], ),
        sa.ForeignKeyConstraint(['connected_business_id'], ['business_profiles.id'], ),
        sa.ForeignKeyConstraint(['constituency_id'], ['constituencies.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_business_connections_business_id'), 'business_connections', ['business_id'], unique=False)
    op.create_index(op.f('ix_business_connections_connected_business_id'), 'business_connections', ['connected_business_id'], unique=False)
    op.create_index(op.f('ix_business_connections_constituency_id'), 'business_connections', ['constituency_id'], unique=False)

    # Create youth_profiles table
    op.create_table('youth_profiles',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('youth_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('constituency_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('ward_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('date_of_birth', sa.DateTime(), nullable=True),
        sa.Column('education_level', sa.String(length=100), nullable=True),
        sa.Column('field_of_study', sa.String(length=200), nullable=True),
        sa.Column('current_status', sa.String(length=100), nullable=True),
        sa.Column('technical_skills', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('soft_skills', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('interests', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('hobbies', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('career_goals', sa.String(length=500), nullable=True),
        sa.Column('preferred_industries', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('job_search_status', sa.String(length=100), nullable=True),
        sa.Column('entrepreneur_interest', sa.Boolean(), nullable=True),
        sa.Column('volunteer_interest', sa.Boolean(), nullable=True),
        sa.Column('social_issues', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('leadership_roles', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('preferred_language', sa.String(length=50), nullable=True),
        sa.Column('notification_preferences', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('featured_youth', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('last_active_date', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['constituency_id'], ['constituencies.id'], ),
        sa.ForeignKeyConstraint(['ward_id'], ['wards.id'], ),
        sa.ForeignKeyConstraint(['youth_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_youth_profiles_constituency_id'), 'youth_profiles', ['constituency_id'], unique=False)
    op.create_index(op.f('ix_youth_profiles_ward_id'), 'youth_profiles', ['ward_id'], unique=False)
    op.create_index(op.f('ix_youth_profiles_youth_id'), 'youth_profiles', ['youth_id'], unique=False)

    # Create youth_programs table
    op.create_table('youth_programs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('program_type', sa.Enum('education', 'skill_development', 'sports', 'cultural', 'environment', 'health', 'leadership', 'entrepreneurship', 'social_service', 'technology', 'arts', 'other', name='program_type'), nullable=False),
        sa.Column('constituency_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organizer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('partner_organizations', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('start_date', sa.DateTime(), nullable=False),
        sa.Column('end_date', sa.DateTime(), nullable=False),
        sa.Column('application_deadline', sa.DateTime(), nullable=True),
        sa.Column('duration_weeks', sa.Integer(), nullable=True),
        sa.Column('max_participants', sa.Integer(), nullable=True),
        sa.Column('min_age', sa.Integer(), nullable=True),
        sa.Column('max_age', sa.Integer(), nullable=True),
        sa.Column('education_requirements', sa.String(length=200), nullable=True),
        sa.Column('skill_requirements', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('venue', sa.String(length=500), nullable=True),
        sa.Column('is_online', sa.Boolean(), nullable=True),
        sa.Column('is_hybrid', sa.Boolean(), nullable=True),
        sa.Column('meeting_link', sa.String(length=500), nullable=True),
        sa.Column('benefits', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('certification_offered', sa.Boolean(), nullable=True),
        sa.Column('certificate_type', sa.String(length=200), nullable=True),
        sa.Column('placement_assistance', sa.Boolean(), nullable=True),
        sa.Column('stipend_amount', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('is_featured', sa.Boolean(), nullable=True),
        sa.Column('program_photos', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('program_videos', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('resource_materials', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('application_count', sa.Integer(), nullable=True),
        sa.Column('selected_count', sa.Integer(), nullable=True),
        sa.Column('completion_count', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['constituency_id'], ['constituencies.id'], ),
        sa.ForeignKeyConstraint(['organizer_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_youth_programs_constituency_id'), 'youth_programs', ['constituency_id'], unique=False)
    op.create_index(op.f('ix_youth_programs_organizer_id'), 'youth_programs', ['organizer_id'], unique=False)
    op.create_index(op.f('ix_youth_programs_program_type'), 'youth_programs', ['program_type'], unique=False)

    # Create program_participations table
    op.create_table('program_participations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('youth_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('program_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('constituency_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('application_date', sa.DateTime(), nullable=True),
        sa.Column('application_status', sa.String(length=50), nullable=True),
        sa.Column('selection_date', sa.DateTime(), nullable=True),
        sa.Column('attendance_percentage', sa.Float(), nullable=True),
        sa.Column('completion_status', sa.String(length=50), nullable=True),
        sa.Column('completion_date', sa.DateTime(), nullable=True),
        sa.Column('performance_rating', sa.String(length=10), nullable=True),
        sa.Column('skills_acquired', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('projects_completed', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('youth_feedback', sa.Text(), nullable=True),
        sa.Column('organizer_feedback', sa.Text(), nullable=True),
        sa.Column('certificate_issued', sa.Boolean(), nullable=True),
        sa.Column('certificate_url', sa.String(length=500), nullable=True),
        sa.Column('placement_status', sa.String(length=100), nullable=True),
        sa.Column('placement_company', sa.String(length=200), nullable=True),
        sa.Column('startup_founded', sa.Boolean(), nullable=True),
        sa.Column('startup_details', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['constituency_id'], ['constituencies.id'], ),
        sa.ForeignKeyConstraint(['program_id'], ['youth_programs.id'], ),
        sa.ForeignKeyConstraint(['youth_id'], ['youth_profiles.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_program_participations_constituency_id'), 'program_participations', ['constituency_id'], unique=False)
    op.create_index(op.f('ix_program_participations_program_id'), 'program_participations', ['program_id'], unique=False)
    op.create_index(op.f('ix_program_participations_youth_id'), 'program_participations', ['youth_id'], unique=False)

    # Create career_requests table
    op.create_table('career_requests',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('youth_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('constituency_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('career_field', sa.Enum('engineering', 'medical', 'management', 'law', 'civil_services', 'defense', 'agriculture', 'science', 'arts', 'commerce', 'vocational', 'entrepreneurship', 'other', name='career_field'), nullable=False),
        sa.Column('request_type', sa.String(length=100), nullable=True),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('current_education', sa.String(length=200), nullable=True),
        sa.Column('target_companies', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('salary_expectation', sa.Float(), nullable=True),
        sa.Column('preferred_location', sa.String(length=200), nullable=True),
        sa.Column('relevant_skills', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('certifications', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('work_experience', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('portfolio_url', sa.String(length=500), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('priority', sa.String(length=50), nullable=True),
        sa.Column('urgency_level', sa.String(length=50), nullable=True),
        sa.Column('guidance_provided', sa.Text(), nullable=True),
        sa.Column('training_suggested', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('job_opportunities', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('internship_opportunities', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('mentor_assigned', sa.String(), nullable=True),
        sa.Column('placement_achieved', sa.Boolean(), nullable=True),
        sa.Column('placed_company', sa.String(length=200), nullable=True),
        sa.Column('placed_position', sa.String(length=200), nullable=True),
        sa.Column('placed_salary', sa.Float(), nullable=True),
        sa.Column('resume_url', sa.String(length=500), nullable=True),
        sa.Column('certificates_urls', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['constituency_id'], ['constituencies.id'], ),
        sa.ForeignKeyConstraint(['mentor_assigned'], ['users.id'], ),
        sa.ForeignKeyConstraint(['youth_id'], ['youth_profiles.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_career_requests_constituency_id'), 'career_requests', ['constituency_id'], unique=False)
    op.create_index(op.f('ix_career_requests_career_field'), 'career_requests', ['career_field'], unique=False)
    op.create_index(op.f('ix_career_requests_youth_id'), 'career_requests', ['youth_id'], unique=False)

    # Create mentorship_connections table
    op.create_table('mentorship_connections',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('youth_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('mentor_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('constituency_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('mentorship_area', sa.String(length=200), nullable=True),
        sa.Column('goals', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('duration_months', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('start_date', sa.DateTime(), nullable=True),
        sa.Column('end_date', sa.DateTime(), nullable=True),
        sa.Column('session_count', sa.Integer(), nullable=True),
        sa.Column('last_session_date', sa.DateTime(), nullable=True),
        sa.Column('total_hours', sa.Float(), nullable=True),
        sa.Column('progress_notes', sa.Text(), nullable=True),
        sa.Column('achievements', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('youth_feedback', sa.Text(), nullable=True),
        sa.Column('mentor_feedback', sa.Text(), nullable=True),
        sa.Column('goals_achieved', sa.Integer(), nullable=True),
        sa.Column('career_progress', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['constituency_id'], ['constituencies.id'], ),
        sa.ForeignKeyConstraint(['mentor_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['youth_id'], ['youth_profiles.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_mentorship_connections_constituency_id'), 'mentorship_connections', ['constituency_id'], unique=False)
    op.create_index(op.f('ix_mentorship_connections_mentor_id'), 'mentorship_connections', ['mentor_id'], unique=False)
    op.create_index(op.f('ix_mentorship_connections_youth_id'), 'mentorship_connections', ['youth_id'], unique=False)

    # Create training_programs table
    op.create_table('training_programs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('training_category', sa.String(length=100), nullable=True),
        sa.Column('constituency_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('trainer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('training_partner', sa.String(length=200), nullable=True),
        sa.Column('start_date', sa.DateTime(), nullable=False),
        sa.Column('end_date', sa.DateTime(), nullable=False),
        sa.Column('duration_hours', sa.Integer(), nullable=True),
        sa.Column('session_frequency', sa.String(length=100), nullable=True),
        sa.Column('max_participants', sa.Integer(), nullable=True),
        sa.Column('min_participants', sa.Integer(), nullable=True),
        sa.Column('prerequisites', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('venue', sa.String(length=500), nullable=True),
        sa.Column('is_online', sa.Boolean(), nullable=True),
        sa.Column('meeting_link', sa.String(length=500), nullable=True),
        sa.Column('certification_offered', sa.Boolean(), nullable=True),
        sa.Column('certificate_issuer', sa.String(length=200), nullable=True),
        sa.Column('training_cost', sa.Float(), nullable=True),
        sa.Column('cost_sponsorship', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('is_free', sa.Boolean(), nullable=True),
        sa.Column('enrollment_count', sa.Integer(), nullable=True),
        sa.Column('completion_count', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['constituency_id'], ['constituencies.id'], ),
        sa.ForeignKeyConstraint(['trainer_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_training_programs_constituency_id'), 'training_programs', ['constituency_id'], unique=False)
    op.create_index(op.f('ix_training_programs_trainer_id'), 'training_programs', ['trainer_id'], unique=False)

    # Create training_participations table
    op.create_table('training_participations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('participant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('training_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('constituency_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('enrollment_date', sa.DateTime(), nullable=True),
        sa.Column('enrollment_status', sa.String(length=50), nullable=True),
        sa.Column('completion_date', sa.DateTime(), nullable=True),
        sa.Column('attendance_percentage', sa.Float(), nullable=True),
        sa.Column('assessment_score', sa.Float(), nullable=True),
        sa.Column('skills_acquired', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('participant_feedback', sa.Text(), nullable=True),
        sa.Column('trainer_feedback', sa.Text(), nullable=True),
        sa.Column('certificate_issued', sa.Boolean(), nullable=True),
        sa.Column('certificate_url', sa.String(length=500), nullable=True),
        sa.Column('income_improvement', sa.Float(), nullable=True),
        sa.Column('business_improvement', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['constituency_id'], ['constituencies.id'], ),
        sa.ForeignKeyConstraint(['participant_id'], ['farmer_profiles.id'], ),
        sa.ForeignKeyConstraint(['training_id'], ['training_programs.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_training_participations_constituency_id'), 'training_participations', ['constituency_id'], unique=False)
    op.create_index(op.f('ix_training_participations_participant_id'), 'training_participations', ['participant_id'], unique=False)
    op.create_index(op.f('ix_training_participations_training_id'), 'training_participations', ['training_id'], unique=False)


def downgrade():
    # Drop all tables in reverse order
    op.drop_table('training_participations')
    op.drop_table('training_programs')
    op.drop_table('mentorship_connections')
    op.drop_table('career_requests')
    op.drop_table('program_participations')
    op.drop_table('youth_programs')
    op.drop_table('youth_profiles')
    op.drop_table('business_connections')
    op.drop_table('business_requests')
    op.drop_table('business_profiles')
    op.drop_table('market_listings')
    op.drop_table('crop_requests')
    op.drop_table('farmer_profiles')
    
    # Drop enums
    op.execute("DROP TYPE IF EXISTS career_field")
    op.execute("DROP TYPE IF EXISTS program_type")
    op.execute("DROP TYPE IF EXISTS business_size")
    op.execute("DROP TYPE IF EXISTS business_category")
    op.execute("DROP TYPE IF EXISTS farming_type")
    op.execute("DROP TYPE IF EXISTS crop_type")
