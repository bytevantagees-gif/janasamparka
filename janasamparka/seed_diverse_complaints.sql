-- ============================================================================
-- SEED DIVERSE COMPLAINTS ACROSS ALL REGIONS
-- Ensures every ward, constituency, department has complaints
-- Balanced distribution across all statuses
-- ============================================================================

-- Delete existing complaints to start fresh (optional - comment out to keep existing)
-- DELETE FROM media WHERE complaint_id IN (SELECT id FROM complaints);
-- DELETE FROM case_notes WHERE complaint_id IN (SELECT id FROM complaints);
-- DELETE FROM complaints;

DO $$
DECLARE
    ward_rec RECORD;
    dept_rec RECORD;
    constituency_rec RECORD;
    citizen_id uuid;
    officer_id uuid;
    gp_id uuid;
    complaint_num int := 0;
    
    complaint_categories text[] := ARRAY['water', 'roads', 'sanitation', 'electricity', 'drainage', 'health', 'education', 'utilities'];
    priorities text[] := ARRAY['low', 'medium', 'high', 'urgent'];
    statuses text[] := ARRAY['submitted', 'assigned', 'in_progress', 'resolved', 'closed', 'rejected'];
    
    titles_water text[] := ARRAY[
        'Water Supply Disruption', 
        'Contaminated Water Issue',
        'Low Water Pressure',
        'Broken Water Pipeline',
        'Water Tank Maintenance'
    ];
    
    titles_roads text[] := ARRAY[
        'Pothole Repair Needed',
        'Road Resurfacing Required',
        'Street Light Not Working',
        'Road Widening Needed',
        'Speed Breaker Installation'
    ];
    
    titles_sanitation text[] := ARRAY[
        'Garbage Not Collected',
        'Sewage Overflow',
        'Public Toilet Maintenance',
        'Waste Segregation Issue',
        'Drain Cleaning Required'
    ];
    
    titles_electricity text[] := ARRAY[
        'Power Cut Issue',
        'Transformer Malfunction',
        'Voltage Fluctuation',
        'Street Light Repair',
        'Power Line Damage'
    ];
    
    titles_drainage text[] := ARRAY[
        'Drainage Blocked',
        'Stormwater Flooding',
        'Manhole Cover Missing',
        'Drain Construction Needed',
        'Rainwater Harvesting'
    ];
    
    titles_health text[] := ARRAY[
        'Health Center Medicine Shortage',
        'Ambulance Service Delay',
        'Vaccination Drive Request',
        'Health Camp Needed',
        'Hospital Equipment Issue'
    ];
    
    titles_education text[] := ARRAY[
        'School Building Repair',
        'Teacher Shortage',
        'Playground Maintenance',
        'Library Resources Needed',
        'Lab Equipment Required'
    ];
    
    titles_utilities text[] := ARRAY[
        'Park Maintenance',
        'Community Hall Repair',
        'Bus Stop Construction',
        'Public Parking Issue',
        'Market Area Improvement'
    ];
BEGIN
    -- Create 3-5 complaints for EVERY ward
    FOR ward_rec IN 
        SELECT w.id, w.name, w.ward_type, w.constituency_id, w.gram_panchayat_id, w.taluk_panchayat_id
        FROM wards w
        ORDER BY w.name
    LOOP
        -- Create 3-5 complaints per ward
        FOR i IN 1..3 + (complaint_num % 3) LOOP
            complaint_num := complaint_num + 1;
            
            -- Get random citizen from this constituency
            SELECT u.id INTO citizen_id 
            FROM users u 
            WHERE u.role = 'citizen' 
                AND u.constituency_id = ward_rec.constituency_id
            ORDER BY random() 
            LIMIT 1;
            
            -- If no citizen in this constituency, get any citizen
            IF citizen_id IS NULL THEN
                SELECT id INTO citizen_id FROM users WHERE role = 'citizen' ORDER BY random() LIMIT 1;
            END IF;
            
            -- Get random department
            SELECT id INTO dept_rec FROM departments ORDER BY random() LIMIT 1;
            
            -- Get random officer (60% chance of assignment)
            IF random() > 0.4 THEN
                SELECT id INTO officer_id FROM users WHERE role = 'department_officer' ORDER BY random() LIMIT 1;
            ELSE
                officer_id := NULL;
            END IF;
            
            -- Determine category based on complaint number
            DECLARE
                cat_index int := (complaint_num % 8);
                category text := complaint_categories[cat_index + 1];
                status_index int := (complaint_num % 6);
                status_val text := statuses[status_index + 1];
                priority_index int := (complaint_num % 4);
                priority_val text := priorities[priority_index + 1];
                title_text text;
                description_text text;
            BEGIN
                -- Select title based on category
                CASE category
                    WHEN 'water' THEN 
                        title_text := titles_water[(complaint_num % 5) + 1];
                        description_text := 'Water supply issue affecting residents. Requires immediate attention from water department.';
                    WHEN 'roads' THEN
                        title_text := titles_roads[(complaint_num % 5) + 1];
                        description_text := 'Road condition is poor. Safety hazard for vehicles and pedestrians. Needs urgent repair.';
                    WHEN 'sanitation' THEN
                        title_text := titles_sanitation[(complaint_num % 5) + 1];
                        description_text := 'Sanitation problem causing health concerns. Immediate action required by sanitation department.';
                    WHEN 'electricity' THEN
                        title_text := titles_electricity[(complaint_num % 5) + 1];
                        description_text := 'Power supply issue affecting daily life. Requires electrical department intervention.';
                    WHEN 'drainage' THEN
                        title_text := titles_drainage[(complaint_num % 5) + 1];
                        description_text := 'Drainage problem causing waterlogging. Needs public works department attention.';
                    WHEN 'health' THEN
                        title_text := titles_health[(complaint_num % 5) + 1];
                        description_text := 'Health facility issue affecting community welfare. Health department action needed.';
                    WHEN 'education' THEN
                        title_text := titles_education[(complaint_num % 5) + 1];
                        description_text := 'Educational facility needs improvement. Education department intervention required.';
                    ELSE
                        title_text := titles_utilities[(complaint_num % 5) + 1];
                        description_text := 'Public utility issue affecting residents. Concerned department should take action.';
                END CASE;
                
                -- Insert complaint
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
                    ward_rec.constituency_id,
                    ward_rec.gram_panchayat_id,
                    citizen_id,
                    title_text || ' - ' || ward_rec.name,
                    description_text || ' Location: ' || ward_rec.name || '. Ward Type: ' || ward_rec.ward_type || '.',
                    category,
                    12.8 + (random() * 2.0),  -- Karnataka lat range
                    74.8 + (random() * 2.0),  -- Karnataka lng range
                    ward_rec.id,
                    ward_rec.name || ', ' || CASE 
                        WHEN ward_rec.ward_type = 'city_corporation' THEN 'City Area'
                        WHEN ward_rec.ward_type = 'taluk_panchayat' THEN 'Taluk Area'
                        ELSE 'Gram Panchayat Area'
                    END,
                    CASE WHEN status_val != 'submitted' THEN dept_rec ELSE NULL END,
                    CASE WHEN status_val IN ('assigned', 'in_progress') THEN officer_id ELSE NULL END,
                    status_val,
                    priority_val,
                    CASE priority_val
                        WHEN 'urgent' THEN 90.0 + (random() * 10.0)
                        WHEN 'high' THEN 60.0 + (random() * 20.0)
                        WHEN 'medium' THEN 30.0 + (random() * 20.0)
                        ELSE 10.0 + (random() * 15.0)
                    END,
                    (priority_val = 'urgent' AND random() > 0.7),
                    false,
                    0,
                    false,
                    NOW() - INTERVAL '1 day' * (random() * 90),
                    NOW() - INTERVAL '1 day' * (random() * 45),
                    NOW() - INTERVAL '1 day' * (random() * 20),
                    NOW() - INTERVAL '1 day' * (random() * 30)
                );
            END;
        END LOOP;
    END LOOP;
    
    RAISE NOTICE 'Created complaints for all % wards', (SELECT COUNT(*) FROM wards);
END $$;

-- Add media for new complaints
INSERT INTO media (
    id,
    complaint_id,
    url,
    media_type,
    file_size,
    lat,
    lng,
    proof_type,
    photo_type,
    caption,
    uploaded_at,
    uploaded_by
)
SELECT 
    gen_random_uuid(),
    c.id,
    'https://storage.janasamparka.gov.in/media/' || c.id::text || '_' || n || 
    CASE WHEN random() > 0.75 THEN '.mp4' ELSE '.jpg' END,
    CASE WHEN random() > 0.75 THEN 'video' ELSE 'photo' END,
    CASE WHEN random() > 0.75 THEN 1024 * 1024 * (5 + random() * 20) ELSE 1024 * (200 + random() * 800) END,
    c.lat,
    c.lng,
    CASE WHEN n = 1 THEN 'before' ELSE 'after' END,
    'site',
    CASE n 
        WHEN 1 THEN 'Photo showing current condition'
        WHEN 2 THEN 'Additional documentation'
        ELSE 'Progress update photo'
    END,
    c.created_at + INTERVAL '1 hour' * n,
    c.user_id
FROM complaints c
CROSS JOIN generate_series(1, 2) n
WHERE random() > 0.35  -- 65% of complaints get media
ORDER BY c.created_at DESC
LIMIT 150;

-- Add case notes for complaints in active states
INSERT INTO case_notes (
    id,
    complaint_id,
    note,
    note_type,
    created_by,
    is_public,
    resets_idle_timer,
    created_at
)
SELECT 
    gen_random_uuid(),
    c.id,
    CASE (random() * 7)::int
        WHEN 0 THEN 'Initial site inspection completed. Issue confirmed.'
        WHEN 1 THEN 'Forwarded to technical team for assessment.'
        WHEN 2 THEN 'Work order issued. Contractor assigned.'
        WHEN 3 THEN 'Work in progress. Expected completion in 7-10 days.'
        WHEN 4 THEN 'Quality inspection done. Work satisfactory.'
        WHEN 5 THEN 'Escalated to senior officer due to urgency.'
        ELSE 'Citizen updated on progress. Follow-up scheduled.'
    END,
    CASE WHEN random() > 0.5 THEN 'department_note' ELSE 'status_update' END,
    COALESCE(
        c.assigned_to,
        (SELECT id FROM users WHERE role = 'department_officer' ORDER BY random() LIMIT 1)
    ),
    CASE WHEN random() > 0.3 THEN true ELSE false END,
    CASE WHEN random() > 0.6 THEN true ELSE false END,
    c.created_at + INTERVAL '1 day' * (1 + random() * 20)
FROM complaints c
WHERE c.status IN ('assigned', 'in_progress', 'resolved', 'closed')
ORDER BY random()
LIMIT 120;

-- ============================================================================
-- SUMMARY REPORTS
-- ============================================================================

SELECT '======================================' as info;
SELECT '     COMPREHENSIVE DATA SUMMARY       ' as info;
SELECT '======================================' as info;

-- Overall counts
SELECT 
    'Total Complaints' as metric,
    COUNT(*)::text as value
FROM complaints
UNION ALL
SELECT 
    'Total Media Items',
    COUNT(*)::text
FROM media
UNION ALL
SELECT 
    'Total Case Notes',
    COUNT(*)::text
FROM case_notes;

SELECT '' as info;
SELECT '=== COMPLAINTS BY STATUS ===' as info;
SELECT 
    status,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1)::text || '%' as percentage
FROM complaints 
GROUP BY status 
ORDER BY count DESC;

SELECT '' as info;
SELECT '=== COMPLAINTS BY CATEGORY ===' as info;
SELECT 
    category,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1)::text || '%' as percentage
FROM complaints 
GROUP BY category 
ORDER BY count DESC;

SELECT '' as info;
SELECT '=== COMPLAINTS BY PRIORITY ===' as info;
SELECT 
    priority,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1)::text || '%' as percentage
FROM complaints 
GROUP BY priority 
ORDER BY count DESC;

SELECT '' as info;
SELECT '=== COMPLAINTS BY WARD TYPE ===' as info;
SELECT 
    w.ward_type,
    COUNT(c.id) as complaints
FROM wards w
LEFT JOIN complaints c ON c.ward_id = w.id
GROUP BY w.ward_type
ORDER BY complaints DESC;

SELECT '' as info;
SELECT '=== COMPLAINTS BY CONSTITUENCY ===' as info;
SELECT 
    co.name as constituency,
    COUNT(c.id) as complaints
FROM constituencies co
LEFT JOIN complaints c ON c.constituency_id = co.id
GROUP BY co.name
ORDER BY complaints DESC;

SELECT '' as info;
SELECT '=== COMPLAINTS BY DEPARTMENT (Top 10) ===' as info;
SELECT 
    d.name as department,
    COUNT(c.id) as complaints
FROM departments d
LEFT JOIN complaints c ON c.dept_id = d.id
GROUP BY d.name
ORDER BY complaints DESC
LIMIT 10;

SELECT '' as info;
SELECT '=== WARDS WITH NO COMPLAINTS (Should be 0) ===' as info;
SELECT 
    w.name,
    w.ward_type,
    COUNT(c.id) as complaints
FROM wards w
LEFT JOIN complaints c ON c.ward_id = w.id
GROUP BY w.id, w.name, w.ward_type
HAVING COUNT(c.id) = 0;

SELECT '' as info;
SELECT '=== WARDS WITH MOST COMPLAINTS (Top 15) ===' as info;
SELECT 
    w.name,
    w.ward_type,
    COUNT(c.id) as complaints
FROM wards w
LEFT JOIN complaints c ON c.ward_id = w.id
GROUP BY w.id, w.name, w.ward_type
ORDER BY complaints DESC
LIMIT 15;

SELECT '' as info;
SELECT '======================================' as info;
SELECT '✅ ALL REGIONS NOW HAVE DIVERSE DATA' as info;
SELECT '======================================' as info;
