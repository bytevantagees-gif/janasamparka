-- ============================================================================
-- COMPREHENSIVE SEED DATA FOR JANASAMPARKA SYSTEM
-- Purpose: Populate all tables with diverse, realistic data for testing
-- Date: October 30, 2025
-- ============================================================================

-- First, let's check what we have and clean up test data if needed
-- We'll keep existing structural data (constituencies, panchayats, wards)
-- But add more varied complaints, users, and related data

-- ============================================================================
-- PART 1: ADDITIONAL USERS (Various Roles for Testing)
-- ============================================================================

-- Admin user (if not exists)
INSERT INTO users (id, firebase_uid, phone, email, name, role, is_active, constituency_id)
SELECT 
    gen_random_uuid(),
    'admin_test_' || gen_random_uuid()::text,
    '+919900000001',
    'admin@janasamparka.gov.in',
    'System Administrator',
    'admin',
    true,
    (SELECT id FROM constituencies LIMIT 1)
WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = 'admin@janasamparka.gov.in');

-- MLA for each constituency
INSERT INTO users (id, firebase_uid, phone, email, name, role, is_active, constituency_id)
SELECT 
    gen_random_uuid(),
    'mla_' || c.id::text,
    '+9199' || (1000000 + ROW_NUMBER() OVER())::text,
    'mla.' || LOWER(REPLACE(c.name, ' ', '.')) || '@janasamparka.gov.in',
    'MLA ' || c.name,
    'mla',
    true,
    c.id
FROM constituencies c
WHERE NOT EXISTS (SELECT 1 FROM users WHERE constituency_id = c.id AND role = 'mla');

-- Moderators (2 per constituency)
INSERT INTO users (id, firebase_uid, phone, email, name, role, is_active, constituency_id)
SELECT 
    gen_random_uuid(),
    'mod_' || c.id::text || '_' || n,
    '+9199' || (2000000 + (ROW_NUMBER() OVER() * 10 + n))::text,
    'moderator' || n || '.' || LOWER(REPLACE(c.name, ' ', '.')) || '@janasamparka.gov.in',
    'Moderator ' || n || ' - ' || c.name,
    'moderator',
    true,
    c.id
FROM constituencies c
CROSS JOIN generate_series(1, 2) n
WHERE NOT EXISTS (
    SELECT 1 FROM users 
    WHERE constituency_id = c.id 
    AND role = 'moderator' 
    AND name LIKE '%Moderator ' || n || '%'
);

-- Ward Officers (1 per ward that has a panchayat link)
INSERT INTO users (id, firebase_uid, phone, email, name, role, is_active, constituency_id, ward_id)
SELECT 
    gen_random_uuid(),
    'ward_officer_' || w.id::text,
    '+9199' || (3000000 + ROW_NUMBER() OVER())::text,
    'ward.officer.' || w.ward_number || '.' || LOWER(REPLACE(w.name, ' ', '.')) || '@janasamparka.gov.in',
    'Ward Officer - ' || w.name || ' (' || w.ward_number || ')',
    'ward_officer',
    true,
    w.constituency_id,
    w.id
FROM wards w
WHERE (w.gram_panchayat_id IS NOT NULL OR w.taluk_panchayat_id IS NOT NULL)
AND NOT EXISTS (SELECT 1 FROM users WHERE ward_id = w.id AND role = 'ward_officer')
LIMIT 15; -- Limit to 15 ward officers for now

-- Department Officers (1 per department)
INSERT INTO users (id, firebase_uid, phone, email, name, role, is_active, constituency_id, department_id)
SELECT 
    gen_random_uuid(),
    'dept_officer_' || d.id::text,
    '+9199' || (4000000 + ROW_NUMBER() OVER())::text,
    'dept.' || LOWER(REPLACE(d.name, ' ', '.')) || '@janasamparka.gov.in',
    'Officer - ' || d.name,
    'department_officer',
    true,
    (SELECT id FROM constituencies LIMIT 1), -- Assign to first constituency
    d.id
FROM departments d
WHERE NOT EXISTS (SELECT 1 FROM users WHERE department_id = d.id AND role = 'department_officer');

-- PDOs (Panchayat Development Officers) for Gram Panchayats
INSERT INTO users (id, firebase_uid, phone, email, name, role, is_active, constituency_id, gram_panchayat_id)
SELECT 
    gen_random_uuid(),
    'pdo_' || gp.id::text,
    '+9199' || (5000000 + ROW_NUMBER() OVER())::text,
    'pdo.' || LOWER(REPLACE(gp.name, ' ', '.')) || '@janasamparka.gov.in',
    'PDO - ' || gp.name,
    'pdo',
    true,
    gp.constituency_id,
    gp.id
FROM gram_panchayats gp
WHERE NOT EXISTS (SELECT 1 FROM users WHERE gram_panchayat_id = gp.id AND role = 'pdo')
LIMIT 10; -- Limit to 10 PDOs

-- Citizens (20 diverse citizens)
INSERT INTO users (id, firebase_uid, phone, email, name, role, is_active, constituency_id, ward_id)
SELECT 
    gen_random_uuid(),
    'citizen_' || n || '_' || gen_random_uuid()::text,
    '+9198' || (1000000 + n * 10000)::text,
    'citizen' || n || '@example.com',
    CASE 
        WHEN n <= 5 THEN 'Rajesh Kumar'
        WHEN n <= 10 THEN 'Priya Shetty'
        WHEN n <= 15 THEN 'Mohammed Ali'
        ELSE 'Lakshmi Devi'
    END || ' - ' || n,
    'citizen',
    true,
    (SELECT id FROM constituencies ORDER BY random() LIMIT 1),
    (SELECT id FROM wards ORDER BY random() LIMIT 1)
FROM generate_series(1, 20) n
WHERE NOT EXISTS (SELECT 1 FROM users WHERE firebase_uid LIKE 'citizen_' || n || '_%');

-- ============================================================================
-- PART 2: COMPLAINTS (Diverse scenarios across all categories and statuses)
-- ============================================================================

-- Get IDs we'll need
DO $$
DECLARE
    v_constituency_id uuid;
    v_ward_id uuid;
    v_citizen_id uuid;
    v_dept_id uuid;
    v_officer_id uuid;
    complaint_categories text[] := ARRAY['water_supply', 'road_maintenance', 'street_lights', 'sanitation', 'drainage', 'electricity', 'health', 'education'];
    priorities text[] := ARRAY['low', 'medium', 'high', 'critical'];
    statuses text[] := ARRAY['pending', 'assigned', 'in_progress', 'resolved', 'closed'];
    locations text[][] := ARRAY[
        ARRAY['MG Road Junction', 'Near City Hospital', 'Main Market Area'],
        ARRAY['Temple Street', 'Bus Stand Road', 'Railway Station'],
        ARRAY['Residency Road', 'Market Cross', 'School Road'],
        ARRAY['Church Street', 'Police Station Road', 'Post Office Junction']
    ];
    i int;
    j int;
BEGIN
    -- Create 50 diverse complaints
    FOR i IN 1..50 LOOP
        -- Get random IDs
        SELECT id INTO v_constituency_id FROM constituencies ORDER BY random() LIMIT 1;
        SELECT id INTO v_ward_id FROM wards WHERE constituency_id = v_constituency_id ORDER BY random() LIMIT 1;
        SELECT id INTO v_citizen_id FROM users WHERE role = 'citizen' ORDER BY random() LIMIT 1;
        SELECT id INTO v_dept_id FROM departments ORDER BY random() LIMIT 1;
        SELECT id INTO v_officer_id FROM users WHERE role = 'department_officer' ORDER BY random() LIMIT 1;
        
        INSERT INTO complaints (
            id,
            title,
            description,
            category,
            priority,
            status,
            location,
            latitude,
            longitude,
            citizen_id,
            constituency_id,
            ward_id,
            department_id,
            assigned_to,
            created_at,
            updated_at,
            last_activity_at,
            resolution_notes,
            resolved_at,
            is_anonymous,
            upvotes,
            downvotes
        )
        VALUES (
            gen_random_uuid(),
            -- Title based on category
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
                WHEN 'water_supply' THEN 'There has been no water supply for the past ' || (1 + (i % 7)) || ' days. The overhead tank appears to be empty and residents are facing severe difficulties. Immediate attention required.'
                WHEN 'road_maintenance' THEN 'The road has developed multiple potholes after recent rains. The condition is worsening and causing accidents. Width approximately ' || (10 + (i % 50)) || ' meters needs repair.'
                WHEN 'street_lights' THEN 'Street lights have not been working for ' || (1 + (i % 14)) || ' days. This is causing safety concerns especially for women and elderly during evening hours.'
                WHEN 'sanitation' THEN 'Garbage has not been collected for ' || (1 + (i % 5)) || ' days. The accumulation is causing health hazards and foul smell in the area. Urgent clearance needed.'
                WHEN 'drainage' THEN 'The drainage system is completely blocked causing water logging. During rains, water enters nearby homes. The blockage appears to be around ' || (i % 100) || ' meters from the main junction.'
                WHEN 'electricity' THEN 'Frequent power cuts lasting ' || (1 + (i % 6)) || ' hours daily. Voltage fluctuation is also damaging electronic appliances. Multiple families affected.'
                WHEN 'health' THEN 'The primary health center lacks basic medicines and the doctor visits only ' || (1 + (i % 3)) || ' days a week. Emergency cases have to travel ' || (10 + (i % 30)) || ' km to the nearest facility.'
                ELSE 'School building has structural damage to classroom number ' || (1 + (i % 12)) || '. Ceiling leaks during rains and poses safety risk to students. Immediate repair required.'
            END,
            -- Category
            complaint_categories[1 + (i % 8)],
            -- Priority
            priorities[1 + (i % 4)],
            -- Status (weighted towards more active cases)
            CASE 
                WHEN i % 5 = 0 THEN 'pending'
                WHEN i % 5 = 1 THEN 'assigned'
                WHEN i % 5 = 2 THEN 'in_progress'
                WHEN i % 5 = 3 THEN 'resolved'
                ELSE 'closed'
            END,
            -- Location
            locations[1 + (i % 4)][1 + (i % 3)],
            -- Latitude (Karnataka range: 11.5 to 18.5)
            12.8 + (random() * 2.0),
            -- Longitude (Karnataka range: 74 to 78)
            74.8 + (random() * 2.0),
            -- Citizen ID
            v_citizen_id,
            -- Constituency ID
            v_constituency_id,
            -- Ward ID
            v_ward_id,
            -- Department ID (if assigned)
            CASE WHEN i % 5 > 0 THEN v_dept_id ELSE NULL END,
            -- Assigned to (if in progress or beyond)
            CASE WHEN i % 5 > 1 THEN v_officer_id ELSE NULL END,
            -- Created at (spread over last 60 days)
            NOW() - INTERVAL '1 day' * (random() * 60),
            -- Updated at
            NOW() - INTERVAL '1 day' * (random() * 30),
            -- Last activity at
            NOW() - INTERVAL '1 day' * (random() * 15),
            -- Resolution notes (if resolved)
            CASE WHEN i % 5 >= 3 THEN 
                'Issue resolved. ' || 
                CASE complaint_categories[1 + (i % 8)]
                    WHEN 'water_supply' THEN 'Water supply restored. Tank cleaned and refilled.'
                    WHEN 'road_maintenance' THEN 'Road repaired. Potholes filled with asphalting work completed.'
                    WHEN 'street_lights' THEN 'Street lights repaired. New LED bulbs installed and tested.'
                    WHEN 'sanitation' THEN 'Garbage cleared. Collection schedule normalized.'
                    WHEN 'drainage' THEN 'Drainage unblocked. Preventive desilting completed.'
                    WHEN 'electricity' THEN 'Power supply stabilized. Transformer upgraded.'
                    WHEN 'health' THEN 'Medicines restocked. Doctor schedule increased to regular visits.'
                    ELSE 'Repair work completed. Structural integrity verified.'
                END
            ELSE NULL END,
            -- Resolved at
            CASE WHEN i % 5 >= 3 THEN NOW() - INTERVAL '1 day' * (random() * 10) ELSE NULL END,
            -- Is anonymous
            (i % 7 = 0),
            -- Upvotes
            floor(random() * 50)::int,
            -- Downvotes  
            floor(random() * 5)::int
        );
    END LOOP;
END $$;

-- ============================================================================
-- PART 3: COMPLAINT ESCALATIONS
-- ============================================================================

-- Add escalations for some complaints
INSERT INTO complaint_escalations (
    id,
    complaint_id,
    escalated_from,
    escalated_to,
    escalation_level,
    escalation_reason,
    escalated_by,
    escalated_at
)
SELECT 
    gen_random_uuid(),
    c.id,
    'gram_panchayat',
    'taluk_panchayat',
    1,
    'Not resolved within SLA timeframe. Issue requires higher-level intervention.',
    (SELECT id FROM users WHERE role = 'pdo' ORDER BY random() LIMIT 1),
    NOW() - INTERVAL '1 day' * (random() * 20)
FROM complaints c
WHERE c.priority IN ('high', 'critical')
AND c.status NOT IN ('resolved', 'closed')
ORDER BY random()
LIMIT 10;

-- ============================================================================
-- PART 4: STATUS LOGS (Audit trail for complaints)
-- ============================================================================

INSERT INTO status_logs (
    id,
    complaint_id,
    old_status,
    new_status,
    changed_by,
    reason,
    created_at
)
SELECT 
    gen_random_uuid(),
    c.id,
    'pending',
    'assigned',
    COALESCE(
        (SELECT id FROM users WHERE role = 'ward_officer' LIMIT 1),
        (SELECT id FROM users WHERE role = 'moderator' LIMIT 1)
    ),
    'Assigned to appropriate department based on complaint category.',
    c.created_at + INTERVAL '1 day'
FROM complaints c
WHERE c.status IN ('assigned', 'in_progress', 'resolved', 'closed')
ORDER BY random()
LIMIT 20;

-- ============================================================================
-- PART 5: POLLS (Community feedback)
-- ============================================================================

INSERT INTO polls (
    id,
    title,
    description,
    constituency_id,
    created_by,
    start_date,
    end_date,
    is_active,
    created_at
)
SELECT 
    gen_random_uuid(),
    poll_data.title,
    poll_data.description,
    c.id,
    (SELECT id FROM users WHERE role = 'mla' AND constituency_id = c.id LIMIT 1),
    NOW() - INTERVAL '5 days',
    NOW() + INTERVAL '25 days',
    true,
    NOW() - INTERVAL '5 days'
FROM constituencies c
CROSS JOIN (
    VALUES 
        ('Priority Development Areas', 'Which area should be prioritized for infrastructure development in the coming quarter?'),
        ('Water Management Survey', 'Rate the current water supply situation in your area and suggest improvements.'),
        ('Road Safety Measures', 'Which roads need immediate safety improvements like speed breakers or signage?')
) AS poll_data(title, description)
LIMIT 6;

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
    option_data.option_text,
    floor(random() * 50)::int
FROM polls p
CROSS JOIN (
    VALUES 
        ('Road Infrastructure'),
        ('Water Supply Network'),
        ('Street Lighting'),
        ('Sanitation Facilities')
) AS option_data(option_text);

-- ============================================================================
-- PART 6: BUDGETS (Ward and Department budgets)
-- ============================================================================

-- Ward Budgets
INSERT INTO ward_budgets (
    id,
    ward_id,
    fiscal_year,
    allocated_amount,
    spent_amount,
    category,
    created_at
)
SELECT 
    gen_random_uuid(),
    w.id,
    '2025-2026',
    1000000 + (random() * 4000000)::numeric(12,2),
    (500000 + (random() * 2000000))::numeric(12,2),
    CASE (row_number() OVER (PARTITION BY w.id)) % 4
        WHEN 0 THEN 'infrastructure'
        WHEN 1 THEN 'sanitation'
        WHEN 2 THEN 'utilities'
        ELSE 'health'
    END,
    NOW() - INTERVAL '90 days'
FROM wards w
CROSS JOIN generate_series(1, 2) -- 2 budget categories per ward
LIMIT 40;

-- Department Budgets
INSERT INTO department_budgets (
    id,
    department_id,
    fiscal_year,
    allocated_amount,
    spent_amount,
    remaining_amount,
    created_at
)
SELECT 
    gen_random_uuid(),
    d.id,
    '2025-2026',
    5000000 + (random() * 20000000)::numeric(12,2),
    (2000000 + (random() * 10000000))::numeric(12,2),
    (3000000 + (random() * 10000000))::numeric(12,2),
    NOW() - INTERVAL '90 days'
FROM departments d;

-- ============================================================================
-- PART 7: CASE NOTES (Internal notes on complaints)
-- ============================================================================

INSERT INTO case_notes (
    id,
    complaint_id,
    note,
    created_by,
    is_internal,
    created_at
)
SELECT 
    gen_random_uuid(),
    c.id,
    note_data.note,
    COALESCE(
        (SELECT id FROM users WHERE role = 'department_officer' ORDER BY random() LIMIT 1),
        (SELECT id FROM users WHERE role = 'moderator' ORDER BY random() LIMIT 1)
    ),
    (random() > 0.3), -- 70% internal notes
    c.created_at + INTERVAL '1 day' * (1 + random() * 10)
FROM complaints c
CROSS JOIN (
    VALUES 
        ('Initial assessment completed. Site inspection scheduled.'),
        ('Consulted with technical team. Material procurement in progress.'),
        ('Work started. Expected completion in 3-5 working days.'),
        ('Progress update: 60% complete. No major obstacles encountered.'),
        ('Quality check done. Work meets specifications.')
) AS note_data(note)
WHERE c.status IN ('assigned', 'in_progress', 'resolved')
ORDER BY random()
LIMIT 50;

-- ============================================================================
-- PART 8: FAQ SOLUTIONS (Knowledge base)
-- ============================================================================

INSERT INTO faq_solutions (
    id,
    category,
    question,
    answer,
    usage_count,
    success_rate,
    created_at
)
VALUES 
    (gen_random_uuid(), 'water_supply', 
     'How do I report a water supply disruption?',
     'You can report water supply issues through the Janasamparka app or website. Go to "File Complaint", select "Water Supply" category, provide your location and description. Ward office will respond within 24 hours.',
     145, 0.87, NOW() - INTERVAL '180 days'),
    
    (gen_random_uuid(), 'road_maintenance',
     'What is the process for pothole repair?',
     'After complaint registration, our team conducts site inspection within 48 hours. For potholes smaller than 1 square meter, repair is completed in 3-5 days. Larger areas are scheduled in the quarterly road maintenance plan.',
     203, 0.92, NOW() - INTERVAL '150 days'),
    
    (gen_random_uuid(), 'street_lights',
     'Street light not working near my house, what to do?',
     'Report the non-functional street light with specific location (pole number if visible). Our electrician team addresses street light issues within 72 hours. If the entire area is affected, it may indicate a transformer issue.',
     178, 0.85, NOW() - INTERVAL '120 days'),
    
    (gen_random_uuid(), 'sanitation',
     'Garbage collection schedule in my area?',
     'Garbage collection schedules vary by ward type: Urban wards - Daily collection (except Sundays), Semi-urban - 3 times per week, Rural - 2 times per week. Check your ward details page for specific schedule.',
     267, 0.91, NOW() - INTERVAL '200 days'),
    
    (gen_random_uuid(), 'drainage',
     'How to report drainage blockage?',
     'Use the app to mark the exact location of blockage on the map. Include photos if possible. Drainage clearance priority: Main roads (24 hrs), Residential streets (48 hrs), Internal lanes (72 hrs).',
     156, 0.88, NOW() - INTERVAL '100 days');

-- ============================================================================
-- SUMMARY QUERIES
-- ============================================================================

-- Print summary
DO $$
DECLARE
    v_constituencies int;
    v_wards int;
    v_departments int;
    v_users int;
    v_complaints int;
    v_polls int;
BEGIN
    SELECT COUNT(*) INTO v_constituencies FROM constituencies;
    SELECT COUNT(*) INTO v_wards FROM wards;
    SELECT COUNT(*) INTO v_departments FROM departments;
    SELECT COUNT(*) INTO v_users FROM users;
    SELECT COUNT(*) INTO v_complaints FROM complaints;
    SELECT COUNT(*) INTO v_polls FROM polls;
    
    RAISE NOTICE '=================================================';
    RAISE NOTICE 'SEED DATA SUMMARY';
    RAISE NOTICE '=================================================';
    RAISE NOTICE 'Constituencies: %', v_constituencies;
    RAISE NOTICE 'Wards: %', v_wards;
    RAISE NOTICE 'Departments: %', v_departments;
    RAISE NOTICE 'Users: %', v_users;
    RAISE NOTICE 'Complaints: %', v_complaints;
    RAISE NOTICE 'Polls: %', v_polls;
    RAISE NOTICE '=================================================';
END $$;

-- Show user distribution by role
SELECT role, COUNT(*) as count 
FROM users 
GROUP BY role 
ORDER BY count DESC;

-- Show complaint distribution by status
SELECT status, COUNT(*) as count 
FROM complaints 
GROUP BY status 
ORDER BY 
    CASE status
        WHEN 'pending' THEN 1
        WHEN 'assigned' THEN 2
        WHEN 'in_progress' THEN 3
        WHEN 'resolved' THEN 4
        WHEN 'closed' THEN 5
    END;

-- Show complaint distribution by category
SELECT category, COUNT(*) as count 
FROM complaints 
GROUP BY category 
ORDER BY count DESC;

COMMIT;
