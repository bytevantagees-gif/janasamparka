-- ============================================================================
-- Seed Additional Department Instances for All Taluks
-- Creates department instances for each taluk across all constituencies
-- ============================================================================

-- Get all taluks and create PWD, Water, and Electricity departments for each
DO $$
DECLARE
    taluk_rec RECORD;
    dept_type_rec RECORD;
    new_dept_id UUID;
    dept_officer_id UUID;
BEGIN
    -- Loop through all taluk panchayats
    FOR taluk_rec IN 
        SELECT 
            tp.id as taluk_id,
            tp.name as taluk_name,
            tp.constituency_id,
            c.name as constituency_name
        FROM taluk_panchayats tp
        JOIN constituencies c ON tp.constituency_id = c.id
    LOOP
        -- Create departments for key types
        FOR dept_type_rec IN 
            SELECT id, name, code 
            FROM department_types 
            WHERE code IN ('PWD', 'WATER', 'ELEC', 'HEALTH', 'ROADS', 'SAN', 'EDUCATION')
        LOOP
            -- Check if department already exists
            IF NOT EXISTS (
                SELECT 1 FROM departments 
                WHERE taluk_panchayat_id = taluk_rec.taluk_id 
                  AND department_type_id = dept_type_rec.id
            ) THEN
                -- Generate new department ID
                new_dept_id := gen_random_uuid();
                
                -- Insert new department
                INSERT INTO departments (
                    id,
                    name,
                    code,
                    constituency_id,
                    taluk_panchayat_id,
                    department_type_id,
                    contact_phone,
                    contact_email,
                    office_address,
                    description,
                    is_active,
                    created_at,
                    updated_at
                )
                VALUES (
                    new_dept_id,
                    taluk_rec.taluk_name || ' ' || dept_type_rec.name,
                    dept_type_rec.code,
                    taluk_rec.constituency_id,
                    taluk_rec.taluk_id,
                    dept_type_rec.id,
                    '+91' || LPAD((8000000000 + (RANDOM() * 999999999)::BIGINT)::TEXT, 10, '0'),
                    LOWER(REPLACE(taluk_rec.taluk_name, ' ', '.')) || '.' || LOWER(dept_type_rec.code) || '@karnataka.gov.in',
                    dept_type_rec.name || ' Office, ' || taluk_rec.taluk_name || ', ' || taluk_rec.constituency_name || ', Karnataka',
                    dept_type_rec.name || ' for ' || taluk_rec.taluk_name || ' Taluk',
                    true,
                    NOW(),
                    NOW()
                );
                
                -- Create a department officer for this department
                dept_officer_id := gen_random_uuid();
                
                INSERT INTO users (
                    id,
                    name,
                    phone,
                    email,
                    role,
                    constituency_id,
                    department_id,
                    is_active,
                    created_at,
                    updated_at
                )
                VALUES (
                    dept_officer_id,
                    'Officer - ' || taluk_rec.taluk_name || ' ' || dept_type_rec.code,
                    '+91' || LPAD((9900000000 + (RANDOM() * 99999999)::BIGINT)::TEXT, 10, '0'),
                    LOWER(REPLACE(taluk_rec.taluk_name, ' ', '.')) || '.' || LOWER(dept_type_rec.code) || '.officer@karnataka.gov.in',
                    'department_officer',
                    taluk_rec.constituency_id,
                    new_dept_id,
                    'active',
                    NOW(),
                    NOW()
                );
                
                -- Assign this officer as the department head
                UPDATE departments 
                SET head_officer_id = dept_officer_id
                WHERE id = new_dept_id;
                
                RAISE NOTICE 'Created: % (Taluk: %)', dept_type_rec.name, taluk_rec.taluk_name;
            END IF;
        END LOOP;
    END LOOP;
    
    -- Create departments for Gram Panchayats (only PWD and Water)
    FOR taluk_rec IN 
        SELECT 
            gp.id as gp_id,
            gp.name as gp_name,
            gp.constituency_id,
            c.name as constituency_name
        FROM gram_panchayats gp
        JOIN constituencies c ON gp.constituency_id = c.id
        LIMIT 15  -- Create for first 15 GPs
    LOOP
        FOR dept_type_rec IN 
            SELECT id, name, code 
            FROM department_types 
            WHERE code IN ('PWD', 'WATER')
        LOOP
            IF NOT EXISTS (
                SELECT 1 FROM departments 
                WHERE gram_panchayat_id = taluk_rec.gp_id 
                  AND department_type_id = dept_type_rec.id
            ) THEN
                new_dept_id := gen_random_uuid();
                
                INSERT INTO departments (
                    id,
                    name,
                    code,
                    constituency_id,
                    gram_panchayat_id,
                    department_type_id,
                    contact_phone,
                    contact_email,
                    office_address,
                    description,
                    is_active,
                    created_at,
                    updated_at
                )
                VALUES (
                    new_dept_id,
                    taluk_rec.gp_name || ' ' || dept_type_rec.name,
                    dept_type_rec.code,
                    taluk_rec.constituency_id,
                    taluk_rec.gp_id,
                    dept_type_rec.id,
                    '+91' || LPAD((8100000000 + (RANDOM() * 899999999)::BIGINT)::TEXT, 10, '0'),
                    LOWER(REPLACE(taluk_rec.gp_name, ' ', '.')) || '.' || LOWER(dept_type_rec.code) || '@karnataka.gov.in',
                    dept_type_rec.name || ' Office, ' || taluk_rec.gp_name || ', Karnataka',
                    dept_type_rec.name || ' for ' || taluk_rec.gp_name,
                    true,
                    NOW(),
                    NOW()
                );
                
                dept_officer_id := gen_random_uuid();
                
                INSERT INTO users (
                    id,
                    name,
                    phone,
                    email,
                    role,
                    constituency_id,
                    department_id,
                    is_active,
                    created_at,
                    updated_at
                )
                VALUES (
                    dept_officer_id,
                    'Officer - ' || taluk_rec.gp_name || ' ' || dept_type_rec.code,
                    '+91' || LPAD((9910000000 + (RANDOM() * 89999999)::BIGINT)::TEXT, 10, '0'),
                    LOWER(REPLACE(taluk_rec.gp_name, ' ', '.')) || '.' || LOWER(dept_type_rec.code) || '.officer@karnataka.gov.in',
                    'department_officer',
                    taluk_rec.constituency_id,
                    new_dept_id,
                    'active',
                    NOW(),
                    NOW()
                );
                
                UPDATE departments 
                SET head_officer_id = dept_officer_id
                WHERE id = new_dept_id;
                
                RAISE NOTICE 'Created GP Dept: % (GP: %)', dept_type_rec.name, taluk_rec.gp_name;
            END IF;
        END LOOP;
    END LOOP;
END $$;

-- Summary
SELECT '=== DEPARTMENT SEEDING SUMMARY ===' as info;

SELECT 
    'Total Department Types' as metric,
    COUNT(*) as count
FROM department_types;

SELECT 
    'Total Departments' as metric,
    COUNT(*) as count
FROM departments;

SELECT 
    'Departments with Heads' as metric,
    COUNT(*) as count
FROM departments 
WHERE head_officer_id IS NOT NULL;

SELECT 
    'Total Department Officers' as metric,
    COUNT(*) as count
FROM users 
WHERE role = 'department_officer';

-- Department distribution by type
SELECT '=== DEPARTMENTS BY TYPE ===' as info;

SELECT 
    dt.name as department_type,
    dt.code,
    COUNT(d.id) as count
FROM department_types dt
LEFT JOIN departments d ON d.department_type_id = dt.id
GROUP BY dt.id, dt.name, dt.code
ORDER BY count DESC;

-- Department distribution by jurisdiction
SELECT '=== DEPARTMENTS BY JURISDICTION ===' as info;

SELECT 
    CASE 
        WHEN gram_panchayat_id IS NOT NULL THEN 'Gram Panchayat'
        WHEN taluk_panchayat_id IS NOT NULL THEN 'Taluk Panchayat'
        WHEN city_corporation_id IS NOT NULL THEN 'City Corporation'
        WHEN zilla_panchayat_id IS NOT NULL THEN 'Zilla Panchayat'
        ELSE 'Constituency Level'
    END as jurisdiction_type,
    COUNT(*) as department_count
FROM departments
GROUP BY jurisdiction_type
ORDER BY department_count DESC;

-- Sample departments with heads
SELECT '=== SAMPLE DEPARTMENTS ===' as info;

SELECT 
    d.name as department_name,
    dt.name as type,
    u.name as head_officer,
    CASE 
        WHEN d.gram_panchayat_id IS NOT NULL THEN 'GP'
        WHEN d.taluk_panchayat_id IS NOT NULL THEN 'TP'
        ELSE 'Other'
    END as level
FROM departments d
JOIN department_types dt ON d.department_type_id = dt.id
LEFT JOIN users u ON d.head_officer_id = u.id
ORDER BY d.created_at DESC
LIMIT 15;
