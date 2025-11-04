-- ============================================================================
-- SEED COMPLAINTS AND RELATED DATA
-- Focused on complaints with correct schema matching
-- ============================================================================

-- Get a sample of IDs for foreign keys
DO $$
DECLARE
    v_constituency_id uuid;
    v_ward_id uuid;
    v_user_id uuid;
    v_dept_id uuid;
    v_officer_id uuid;
    v_gp_id uuid;
    complaint_categories text[] := ARRAY['water', 'roads', 'sanitation', 'electricity', 'drainage', 'health', 'education', 'utilities'];
    priorities text[] := ARRAY['low', 'medium', 'high', 'urgent'];
    statuses text[] := ARRAY['submitted', 'assigned', 'in_progress', 'resolved', 'closed', 'rejected'];
    locations text[][] := ARRAY[
        ARRAY['MG Road', 'Market Area', 'Bus Stand'],
        ARRAY['Temple St', 'School Rd', 'Hospital'],
        ARRAY['Main Road', 'Cross Rd', 'Station Rd']
    ];
    i int;
BEGIN
    -- Create 80 complaints
    FOR i IN 1..80 LOOP
        -- Get random IDs for each complaint
        SELECT id INTO v_constituency_id FROM constituencies ORDER BY random() LIMIT 1;
        SELECT id, gram_panchayat_id INTO v_ward_id, v_gp_id FROM wards WHERE constituency_id = v_constituency_id ORDER BY random() LIMIT 1;
        SELECT id INTO v_user_id FROM users WHERE role = 'citizen' ORDER BY random() LIMIT 1;
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
            notes_are_internal,
            created_at,
            updated_at,
            last_activity_at,
            notes_updated_at
        )
        VALUES (
            gen_random_uuid(),
            v_constituency_id,
            v_gp_id,
            v_user_id,
            -- Title
            CASE complaint_categories[1 + (i % 8)]
                WHEN 'water' THEN 'Water Supply Issue - ' || locations[1 + (i % 3)][1 + (i % 3)]
                WHEN 'roads' THEN 'Road Repair Needed - ' || locations[1 + (i % 3)][1 + (i % 3)]
                WHEN 'sanitation' THEN 'Garbage Collection - ' || locations[1 + (i % 3)][1 + (i % 3)]
                WHEN 'electricity' THEN 'Power Supply - ' || locations[1 + (i % 3)][1 + (i % 3)]
                WHEN 'drainage' THEN 'Drainage Blocked - ' || locations[1 + (i % 3)][1 + (i % 3)]
                WHEN 'health' THEN 'Health Facility - ' || locations[1 + (i % 3)][1 + (i % 3)]
                WHEN 'education' THEN 'School Issue - ' || locations[1 + (i % 3)][1 + (i % 3)]
                ELSE 'Utility Problem - ' || locations[1 + (i % 3)][1 + (i % 3)]
            END,
            -- Description
            'Issue reported by citizen. ' || 
            CASE complaint_categories[1 + (i % 8)]
                WHEN 'water' THEN 'Water supply disrupted for ' || (1 + (i % 7)) || ' days. Residents facing difficulties.'
                WHEN 'roads' THEN 'Road has potholes. Width ' || (10 + (i % 30)) || 'm needs repair. Safety hazard.'
                WHEN 'sanitation' THEN 'Garbage not collected for ' || (1 + (i % 5)) || ' days. Health concern.'
                WHEN 'electricity' THEN 'Power cuts for ' || (1 + (i % 8)) || ' hours daily. Voltage issues.'
                WHEN 'drainage' THEN 'Drainage blocked causing flooding. Needs urgent attention.'
                WHEN 'health' THEN 'Health center lacks medicines. Doctor availability limited.'
                WHEN 'education' THEN 'School infrastructure needs repair. Safety concern for students.'
                ELSE 'Utility issue causing inconvenience to residents.'
            END,
            -- Category
            complaint_categories[1 + (i % 8)],
            -- Latitude
            12.8 + (random() * 2.0),
            -- Longitude
            74.8 + (random() * 2.0),
            -- Ward
            v_ward_id,
            -- Location description
            locations[1 + (i % 3)][1 + (i % 3)],
            -- Department (assigned for 60% of complaints)
            CASE WHEN i % 5 > 1 THEN v_dept_id ELSE NULL END,
            -- Assigned to (40% assigned)
            CASE WHEN i % 5 > 2 THEN v_officer_id ELSE NULL END,
            -- Status
            statuses[1 + (i % 6)],
            -- Priority
            priorities[1 + (i % 4)],
            -- Priority score
            25.0 + (random() * 75.0),
            -- Is emergency
            (i % 15 = 0),
            -- Is duplicate
            false,
            -- Duplicate count
            0,
            -- Notes are internal
            false,
            -- Created at (last 90 days)
            NOW() - INTERVAL '1 day' * (random() * 90),
            -- Updated at
            NOW() - INTERVAL '1 day' * (random() * 45),
            -- Last activity at
            NOW() - INTERVAL '1 day' * (random() * 20),
            -- Notes updated at
            NOW() - INTERVAL '1 day' * (random() * 30)
        );
    END LOOP;
    
    RAISE NOTICE 'Created 80 complaints successfully';
END $$;

-- Add media for complaints
INSERT INTO media (
    id,
    complaint_id,
    media_type,
    url,
    thumbnail,
    created_at
)
SELECT 
    gen_random_uuid(),
    c.id,
    CASE WHEN random() > 0.7 THEN 'video' ELSE 'photo' END,
    'https://storage.janasamparka.gov.in/media/' || c.id::text || '_' || n || '.jpg',
    'https://storage.janasamparka.gov.in/thumbs/' || c.id::text || '_thumb.jpg',
    c.created_at + INTERVAL '1 minute' * n
FROM complaints c
CROSS JOIN generate_series(1, 2) n
WHERE random() > 0.4  
LIMIT 100;

-- Add case notes
INSERT INTO case_notes (
    id,
    complaint_id,
    note_type,
    note,
    created_by,
    created_at
)
SELECT 
    gen_random_uuid(),
    c.id,
    CASE WHEN random() > 0.6 THEN 'internal' ELSE 'public' END,
    note_texts.note,
    COALESCE(
        (SELECT id FROM users WHERE role = 'department_officer' ORDER BY random() LIMIT 1),
        (SELECT id FROM users WHERE role = 'moderator' ORDER BY random() LIMIT 1)
    ),
    c.created_at + INTERVAL '1 day' * (1 + random() * 15)
FROM complaints c
CROSS JOIN (
    VALUES 
        ('Initial assessment completed'),
        ('Site inspection done'),
        ('Work in progress'),
        ('Quality check completed')
) AS note_texts(note)
WHERE c.status IN ('assigned', 'in_progress', 'resolved')
ORDER BY random()
LIMIT 50;

-- Summary
SELECT '=== DATA SUMMARY ===' as info;
SELECT 
    'Users' as entity,
    COUNT(*) as total
FROM users
UNION ALL
SELECT 
    'Complaints',
    COUNT(*)
FROM complaints
UNION ALL
SELECT 
    'Media Items',
    COUNT(*)
FROM media
UNION ALL
SELECT 
    'Case Notes',
    COUNT(*)
FROM case_notes;

SELECT '=== COMPLAINT STATUS DISTRIBUTION ===' as info;
SELECT 
    status,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) as percentage
FROM complaints 
GROUP BY status 
ORDER BY count DESC;

SELECT '=== COMPLAINT CATEGORY DISTRIBUTION ===' as info;
SELECT 
    category,
    COUNT(*) as count
FROM complaints 
GROUP BY category 
ORDER BY count DESC;

SELECT '=== COMPLAINT PRIORITY DISTRIBUTION ===' as info;
SELECT 
    priority,
    COUNT(*) as count
FROM complaints 
GROUP BY priority 
ORDER BY count DESC;
