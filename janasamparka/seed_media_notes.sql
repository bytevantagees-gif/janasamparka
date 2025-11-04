-- ============================================================================
-- SEED MEDIA AND CASE NOTES
-- Add realistic media items and case notes to complaints
-- ============================================================================

-- Add media for complaints (photos and videos)
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
    'https://storage.janasamparka.gov.in/media/' || c.id::text || '_' || n || CASE WHEN random() > 0.7 THEN '.mp4' ELSE '.jpg' END,
    CASE WHEN random() > 0.7 THEN 'video' ELSE 'photo' END,
    CASE WHEN random() > 0.7 THEN 1024 * 1024 * (5 + random() * 20) ELSE 1024 * (200 + random() * 800) END,
    c.lat,
    c.lng,
    CASE WHEN random() > 0.5 THEN 'before' ELSE 'after' END,
    CASE WHEN random() > 0.3 THEN 'site' ELSE 'general' END,
    CASE n 
        WHEN 1 THEN 'Site photo showing the issue'
        WHEN 2 THEN 'Additional view of the problem area'
        ELSE 'Supporting documentation'
    END,
    c.created_at + INTERVAL '1 minute' * n,
    c.user_id
FROM complaints c
CROSS JOIN generate_series(1, 2) n
WHERE random() > 0.3  -- 70% of complaints get media
ORDER BY random()
LIMIT 120;

-- Add case notes (internal and public)
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
    note_data.note,
    CASE WHEN random() > 0.6 THEN 'department_note' ELSE 'status_update' END,
    COALESCE(
        c.assigned_to,
        (SELECT id FROM users WHERE role = 'department_officer' ORDER BY random() LIMIT 1),
        (SELECT id FROM users WHERE role = 'moderator' ORDER BY random() LIMIT 1)
    ),
    CASE WHEN random() > 0.4 THEN true ELSE false END,
    CASE WHEN random() > 0.7 THEN true ELSE false END,
    c.created_at + INTERVAL '1 day' * (1 + random() * 15)
FROM complaints c
CROSS JOIN (
    VALUES 
        ('Initial assessment completed. Issue verified on site.'),
        ('Site inspection done. Forwarding to technical team.'),
        ('Work in progress. Expected completion in 7 days.'),
        ('Quality check completed. Issue resolved satisfactorily.'),
        ('Additional resources requested from higher authority.'),
        ('Citizen contacted for additional information.'),
        ('Escalating to senior officer for priority action.'),
        ('Budget allocation approved. Work to commence shortly.')
) AS note_data(note)
WHERE c.status IN ('assigned', 'in_progress', 'resolved', 'closed')
ORDER BY random()
LIMIT 80;

-- Summary
SELECT '=== MEDIA SUMMARY ===' as info;
SELECT 
    media_type,
    COUNT(*) as count,
    ROUND(AVG(file_size)/1024, 0) as avg_size_kb
FROM media 
GROUP BY media_type;

SELECT '=== CASE NOTES SUMMARY ===' as info;
SELECT 
    is_public,
    COUNT(*) as count
FROM case_notes 
GROUP BY is_public;

SELECT '=== FINAL DATA COUNT ===' as info;
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
FROM case_notes
UNION ALL
SELECT 
    'Polls',
    COUNT(*)
FROM polls;
