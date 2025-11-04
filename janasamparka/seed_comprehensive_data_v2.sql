-- ============================================================================
-- CORRECTED COMPREHENSIVE SEED DATA FOR JANASAMPARKA SYSTEM
-- Matches actual database schema
-- Date: October 30, 2025
-- ============================================================================

-- Remove transaction to allow partial updates
-- BEGIN;

-- ============================================================================
-- PART 1: ADDITIONAL USERS (Various Roles for Testing)
-- ============================================================================

-- Admin user
INSERT INTO users (id, phone, email, name, role, is_active, constituency_id, locale_pref, created_at, updated_at)
SELECT 
    gen_random_uuid(),
    '+919900000001',
    'admin@janasamparka.gov.in',
    'System Administrator',
    'admin',
    'active',
    (SELECT id FROM constituencies LIMIT 1),
    'en',
    NOW(),
    NOW()
WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = 'admin@janasamparka.gov.in');

-- MLA for each constituency
INSERT INTO users (id, phone, email, name, role, is_active, constituency_id, locale_pref, created_at, updated_at)
SELECT 
    gen_random_uuid(),
    '+9199' || (1000000 + ROW_NUMBER() OVER())::text,
    'mla.' || LOWER(REPLACE(c.name, ' ', '.')) || '@janasamparka.gov.in',
    'MLA ' || c.name,
    'mla',
    'active',
    c.id,
    'en',
    NOW(),
    NOW()
FROM constituencies c
WHERE NOT EXISTS (SELECT 1 FROM users WHERE constituency_id = c.id AND role = 'mla');

-- Moderators
INSERT INTO users (id, phone, email, name, role, is_active, constituency_id, locale_pref, created_at, updated_at)
SELECT 
    gen_random_uuid(),
    '+9199' || (2000000 + (ROW_NUMBER() OVER()))::text,
    'moderator' || ROW_NUMBER() OVER() || '@janasamparka.gov.in',
    'Moderator ' || ROW_NUMBER() OVER(),
    'moderator',
    'active',
    (SELECT id FROM constituencies ORDER BY random() LIMIT 1),
    'en',
    NOW(),
    NOW()
FROM generate_series(1, 5)
WHERE NOT EXISTS (SELECT 1 FROM users WHERE role = 'moderator' LIMIT 5);

-- Ward Officers (fix email uniqueness)
INSERT INTO users (id, phone, email, name, role, is_active, constituency_id, ward_id, locale_pref, created_at, updated_at)
SELECT 
    gen_random_uuid(),
    '+9199' || (3000000 + ROW_NUMBER() OVER())::text,
    'ward.officer.w' || w.id::text || '@janasamparka.gov.in',
    'Ward Officer - Ward ' || w.ward_number,
    'ward_officer',
    'active',
    w.constituency_id,
    w.id,
    'en',
    NOW(),
    NOW()
FROM wards w
WHERE (w.gram_panchayat_id IS NOT NULL OR w.taluk_panchayat_id IS NOT NULL)
AND NOT EXISTS (SELECT 1 FROM users WHERE ward_id = w.id)
LIMIT 10;

-- Department Officers (fix email uniqueness)
INSERT INTO users (id, phone, email, name, role, is_active, constituency_id, department_id, locale_pref, created_at, updated_at)
SELECT 
    gen_random_uuid(),
    '+9199' || (4000000 + ROW_NUMBER() OVER())::text,
    'dept.officer.d' || d.id::text || '@janasamparka.gov.in',
    'Officer - ' || d.name,
    'department_officer',
    'active',
    (SELECT id FROM constituencies LIMIT 1),
    d.id,
    'en',
    NOW(),
    NOW()
FROM departments d
WHERE NOT EXISTS (SELECT 1 FROM users WHERE department_id = d.id);

-- Citizens (30 diverse citizens)
INSERT INTO users (id, phone, email, name, role, is_active, constituency_id, ward_id, locale_pref, created_at, updated_at)
SELECT 
    gen_random_uuid(),
    '+9198' || (1000000 + n * 10000)::text,
    'citizen' || n || '@example.com',
    CASE 
        WHEN n <= 10 THEN 'Rajesh Kumar ' || n
        WHEN n <= 20 THEN 'Priya Shetty ' || n
        ELSE 'Mohammed Ali ' || n
    END,
    'citizen',
    'active',
    (SELECT id FROM constituencies ORDER BY random() LIMIT 1),
    (SELECT id FROM wards ORDER BY random() LIMIT 1),
    CASE WHEN n % 3 = 0 THEN 'kn' ELSE 'en' END,
    NOW(),
    NOW()
FROM generate_series(1, 30) n
WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = 'citizen' || n || '@example.com');

-- ============================================================================
-- PART 2: COMPLAINTS (Diverse scenarios across all categories and statuses)
-- ============================================================================

DO $$
DECLARE
    v_constituency_id uuid;
    v_ward_id uuid;
    v_citizen_id uuid;
    v_dept_id uuid;
    v_officer_id uuid;
    v_gp_id uuid;
    complaint_categories text[] := ARRAY['water_supply', 'road_maintenance', 'street_lights', 'sanitation', 'drainage', 'electricity', 'health', 'education'];
    priorities text[] := ARRAY['low', 'medium', 'high', 'critical'];
    statuses text[] := ARRAY['submitted', 'under_review', 'approved', 'assigned', 'in_progress', 'completed', 'verified', 'rejected'];
    locations text[][] := ARRAY[
        ARRAY['MG Road Junction', 'Near City Hospital', 'Main Market Area'],
        ARRAY['Temple Street', 'Bus Stand Road', 'Railway Station'],
        ARRAY['Residency Road', 'Market Cross', 'School Road'],
        ARRAY['Church Street', 'Police Station Road', 'Post Office Junction']
    ];
    titles text[][];
    descriptions text[][];
    i int;
BEGIN
    -- Create 60 diverse complaints
    FOR i IN 1..60 LOOP
        -- Get random IDs
        SELECT id INTO v_constituency_id FROM constituencies ORDER BY random() LIMIT 1;
        SELECT id, gram_panchayat_id INTO v_ward_id, v_gp_id FROM wards WHERE constituency_id = v_constituency_id ORDER BY random() LIMIT 1;
        SELECT id INTO v_citizen_id FROM users WHERE role = 'citizen' ORDER BY random() LIMIT 1;
        SELECT id INTO v_dept_id FROM departments ORDER BY random() LIMIT 1;
        SELECT id INTO v_officer_id FROM users WHERE role = 'department_officer' ORDER BY random() LIMIT 1;
        
        INSERT INTO complaints (
            id,
            constituency_id,
            gram_panchayat_id,
            user_id,
            title,
            description,
            category,
            lat,
            lng,
            ward_id,
            location_description,
            dept_id,
            assigned_to,
            status,
            priority,
            priority_score,
            is_emergency,
            is_duplicate,
            duplicate_count,
            created_at,
            updated_at,
            last_activity_at,
            resolved_at,
            notes_are_internal
        )
        VALUES (
            gen_random_uuid(),
            v_constituency_id,
            v_gp_id,
            v_citizen_id,
            -- Title
            CASE complaint_categories[1 + (i % 8)]
                WHEN 'water_supply' THEN 'Water Supply Issue - ' || locations[1 + (i % 4)][1 + (i % 3)]
                WHEN 'road_maintenance' THEN 'Road Repair Needed - ' || locations[1 + (i % 4)][1 + (i % 3)]
                WHEN 'street_lights' THEN 'Street Light Not Working - ' || locations[1 + (i % 4)][1 + (i % 3)]
                WHEN 'sanitation' THEN 'Garbage Collection Issue - ' || locations[1 + (i % 4)][1 + (i % 3)]
                WHEN 'drainage' THEN 'Drainage Blocked - ' || locations[1 + (i % 4)][1 + (i % 3)]
                WHEN 'electricity' THEN 'Power Supply Problem - ' || locations[1 + (i % 4)][1 + (i % 3)]
                WHEN 'health' THEN 'Health Facility Issue - ' || locations[1 + (i % 4)][1 + (i % 3)]
                ELSE 'School Infrastructure - ' || locations[1 + (i % 4)][1 + (i % 3)]
            END,
            -- Description
            CASE complaint_categories[1 + (i % 8)]
                WHEN 'water_supply' THEN 'There has been no water supply for the past ' || (1 + (i % 7)) || ' days. Immediate attention required.'
                WHEN 'road_maintenance' THEN 'The road has developed potholes. Width approximately ' || (10 + (i % 50)) || ' meters needs repair.'
                WHEN 'street_lights' THEN 'Street lights not working for ' || (1 + (i % 14)) || ' days. Safety concerns for residents.'
                WHEN 'sanitation' THEN 'Garbage not collected for ' || (1 + (i % 5)) || ' days. Health hazard developing.'
                WHEN 'drainage' THEN 'Drainage blocked causing water logging. Blockage around ' || (i % 100) || ' meters from junction.'
                WHEN 'electricity' THEN 'Frequent power cuts lasting ' || (1 + (i % 6)) || ' hours daily. Voltage issues.'
                WHEN 'health' THEN 'Health center lacks medicines. Doctor visits only ' || (1 + (i % 3)) || ' days weekly.'
                ELSE 'School building structural damage. Ceiling leaks during rains.'
            END,
            -- Category
            complaint_categories[1 + (i % 8)],
            -- Latitude (Karnataka range)
            12.8 + (random() * 2.0),
            -- Longitude (Karnataka range)
            74.8 + (random() * 2.0),
            -- Ward ID
            v_ward_id,
            -- Location description
            locations[1 + (i % 4)][1 + (i % 3)],
            -- Department ID
            CASE WHEN i % 8 > 1 THEN v_dept_id ELSE NULL END,
            -- Assigned to
            CASE WHEN i % 8 > 3 THEN v_officer_id ELSE NULL END,
            -- Status
            statuses[1 + (i % 8)],
            -- Priority
            priorities[1 + (i % 4)],
            -- Priority score
            25.0 + (random() * 75.0),
            -- Is emergency
            (i % 10 = 0),
            -- Is duplicate
            false,
            -- Duplicate count
            0,
            -- Created at (last 90 days)
            NOW() - INTERVAL '1 day' * (random() * 90),
            -- Updated at
            NOW() - INTERVAL '1 day' * (random() * 45),
            -- Last activity at
            NOW() - INTERVAL '1 day' * (random() * 20),
            -- Resolved at
            CASE WHEN statuses[1 + (i % 8)] IN ('completed', 'verified') 
                THEN NOW() - INTERVAL '1 day' * (random() * 10) 
                ELSE NULL 
            END,
            -- Notes are internal
            false
        );
    END LOOP;
END $$;

-- ============================================================================
-- PART 3: COMPLAINT ESCALATIONS
-- ============================================================================

INSERT INTO complaint_escalations (
    id,
    complaint_id,
    from_entity_type,
    from_entity_id,
    to_entity_type,
    to_entity_id,
    escalation_level,
    reason,
    escalated_by,
    escalated_at
)
SELECT 
    gen_random_uuid(),
    c.id,
    'gram_panchayat',
    c.gram_panchayat_id,
    'taluk_panchayat',
    w.taluk_panchayat_id,
    1,
    'Issue requires higher-level intervention. Not resolved within SLA timeframe.',
    (SELECT id FROM users WHERE role IN ('pdo', 'moderator') ORDER BY random() LIMIT 1),
    NOW() - INTERVAL '1 day' * (random() * 30)
FROM complaints c
JOIN wards w ON c.ward_id = w.id
WHERE c.priority IN ('high', 'critical')
AND c.status NOT IN ('completed', 'verified', 'rejected')
AND c.gram_panchayat_id IS NOT NULL
AND w.taluk_panchayat_id IS NOT NULL
ORDER BY random()
LIMIT 15;

-- ============================================================================
-- PART 4: STATUS LOGS
-- ============================================================================

INSERT INTO status_logs (
    id,
    complaint_id,
    from_status,
    to_status,
    changed_by,
    changed_at
)
SELECT 
    gen_random_uuid(),
    c.id,
    'submitted',
    'under_review',
    (SELECT id FROM users WHERE role IN ('moderator', 'ward_officer') ORDER BY random() LIMIT 1),
    c.created_at + INTERVAL '2 hours'
FROM complaints c
WHERE c.status NOT IN ('submitted')
ORDER BY random()
LIMIT 30;

-- ============================================================================
-- PART 5: MEDIA (Photos/Videos for complaints)
-- ============================================================================

INSERT INTO media (
    id,
    complaint_id,
    media_type,
    media_url,
    thumbnail_url,
    created_at
)
SELECT 
    gen_random_uuid(),
    c.id,
    CASE WHEN random() > 0.7 THEN 'video' ELSE 'photo' END,
    'https://storage.janasamparka.gov.in/media/' || c.id::text || '_' || n || '.jpg',
    'https://storage.janasamparka.gov.in/thumbs/' || c.id::text || '_' || n || '_thumb.jpg',
    c.created_at + INTERVAL '1 minute' * n
FROM complaints c
CROSS JOIN generate_series(1, 2) n
WHERE random() > 0.3 -- 70% of complaints have media
ORDER BY random()
LIMIT 80;

-- ============================================================================
-- PART 6: POLLS
-- ============================================================================

-- Create polls for each constituency
INSERT INTO polls (
    id,
    constituency_id,
    title,
    description,
    created_by,
    start_date,
    end_date,
    is_active,
    created_at
)
SELECT 
    gen_random_uuid(),
    c.id,
    poll_titles.title,
    poll_titles.description,
    (SELECT id FROM users WHERE role = 'mla' AND constituency_id = c.id LIMIT 1),
    NOW() - INTERVAL '10 days',
    NOW() + INTERVAL '20 days',
    true,
    NOW() - INTERVAL '10 days'
FROM constituencies c
CROSS JOIN (
    VALUES 
        ('Infrastructure Priority Survey', 'Help us identify priority areas for development'),
        ('Water Management Feedback', 'Share your experience with water supply in your area'),
        ('Road Safety Assessment', 'Which roads need immediate safety improvements?')
) AS poll_titles(title, description)
LIMIT 9;

-- Add poll options
INSERT INTO poll_options (
    id,
    poll_id,
    option_text,
    vote_count
)
SELECT 
    gen_random_uuid(),
    p.id,
    opt.option_text,
    floor(random() * 100)::int
FROM polls p
CROSS JOIN (
    VALUES 
        ('Excellent'),
        ('Good'),
        ('Average'),
        ('Poor'),
        ('Very Poor')
) AS opt(option_text);

-- ============================================================================
-- PART 7: BUDGETS
-- ============================================================================

-- Ward Budgets
INSERT INTO ward_budgets (
    id,
    ward_id,
    year,
    allocated_amount,
    spent_amount,
    category,
    created_at
)
SELECT 
    gen_random_uuid(),
    w.id,
    2025,
    (1000000 + (random() * 4000000))::numeric(12,2),
    (500000 + (random() * 2000000))::numeric(12,2),
    CASE (row_number() OVER (PARTITION BY w.id)) % 3
        WHEN 0 THEN 'infrastructure'
        WHEN 1 THEN 'sanitation'
        ELSE 'utilities'
    END,
    NOW() - INTERVAL '180 days'
FROM wards w
CROSS JOIN generate_series(1, 2)
WHERE w.gram_panchayat_id IS NOT NULL
LIMIT 40;

-- Department Budgets  
INSERT INTO department_budgets (
    id,
    department_id,
    year,
    allocated_amount,
    spent_amount,
    remaining_amount,
    created_at
)
SELECT 
    gen_random_uuid(),
    d.id,
    2025,
    (5000000 + (random() * 20000000))::numeric(12,2),
    (2000000 + (random() * 10000000))::numeric(12,2),
    (3000000 + (random() * 10000000))::numeric(12,2),
    NOW() - INTERVAL '180 days'
FROM departments d;

-- ============================================================================
-- PART 8: CASE NOTES
-- ============================================================================

INSERT INTO case_notes (
    id,
    complaint_id,
    note,
    created_by,
    created_at
)
SELECT 
    gen_random_uuid(),
    c.id,
    note_texts.note,
    COALESCE(
        (SELECT id FROM users WHERE role = 'department_officer' ORDER BY random() LIMIT 1),
        (SELECT id FROM users WHERE role = 'moderator' ORDER BY random() LIMIT 1)
    ),
    c.created_at + INTERVAL '1 day' * (1 + random() * 20)
FROM complaints c
CROSS JOIN (
    VALUES 
        ('Initial assessment completed. Site inspection scheduled within 48 hours.'),
        ('Technical team consulted. Material procurement initiated.'),
        ('Work in progress. Expected completion within 5 working days.'),
        ('Quality verification done. Work meets required standards.')
) AS note_texts(note)
WHERE c.status IN ('assigned', 'in_progress', 'completed')
ORDER BY random()
LIMIT 70;

-- ============================================================================
-- SUMMARY
-- ============================================================================

DO $$
DECLARE
    v_users int;
    v_complaints int;
    v_escalations int;
    v_polls int;
    v_media int;
BEGIN
    SELECT COUNT(*) INTO v_users FROM users;
    SELECT COUNT(*) INTO v_complaints FROM complaints;
    SELECT COUNT(*) INTO v_escalations FROM complaint_escalations;
    SELECT COUNT(*) INTO v_polls FROM polls;
    SELECT COUNT(*) INTO v_media FROM media;
    
    RAISE NOTICE '=================================================';
    RAISE NOTICE 'COMPREHENSIVE SEED DATA COMPLETE';
    RAISE NOTICE '=================================================';
    RAISE NOTICE 'Total Users: %', v_users;
    RAISE NOTICE 'Total Complaints: %', v_complaints;
    RAISE NOTICE 'Total Escalations: %', v_escalations;
    RAISE NOTICE 'Total Polls: %', v_polls;
    RAISE NOTICE 'Total Media Items: %', v_media;
    RAISE NOTICE '=================================================';
END $$;

-- Show distributions
SELECT '=== USER DISTRIBUTION ===' as info;
SELECT role, COUNT(*) as count 
FROM users 
GROUP BY role 
ORDER BY count DESC;

SELECT '=== COMPLAINT STATUS DISTRIBUTION ===' as info;
SELECT status, COUNT(*) as count 
FROM complaints 
GROUP BY status 
ORDER BY count DESC;

SELECT '=== COMPLAINT CATEGORY DISTRIBUTION ===' as info;
SELECT category, COUNT(*) as count 
FROM complaints 
GROUP BY category 
ORDER BY count DESC;

SELECT '=== COMPLAINT PRIORITY DISTRIBUTION ===' as info;
SELECT priority, COUNT(*) as count 
FROM complaints 
GROUP BY priority 
ORDER BY count DESC;

-- COMMIT;
