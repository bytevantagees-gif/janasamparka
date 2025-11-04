-- ============================================================================
-- Department Hierarchical Structure Migration
-- Creates department_types table and links existing departments
-- ============================================================================

-- Step 1: Create department_types table
CREATE TABLE IF NOT EXISTS department_types (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    code VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    icon VARCHAR(50),
    color VARCHAR(20),
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_department_types_code ON department_types(code);
CREATE INDEX IF NOT EXISTS ix_department_types_is_active ON department_types(is_active);

-- Step 2: Insert standard Karnataka department types
INSERT INTO department_types (name, code, description, icon, color, display_order) VALUES
('Public Works Department', 'PWD', 'Infrastructure, roads, buildings, bridges', 'construction', '#FF6B35', 1),
('Water Supply & Drainage', 'WATER', 'Water supply, drainage systems, sanitation', 'water_drop', '#2196F3', 2),
('Electricity Department', 'ELEC', 'Power supply, electrical infrastructure', 'bolt', '#FFC107', 3),
('Health & Sanitation', 'HEALTH', 'Public health, sanitation, waste management', 'medical_services', '#4CAF50', 4),
('Revenue & Administration', 'REVENUE', 'Revenue collection, land records, administration', 'account_balance', '#9C27B0', 5),
('Education Department', 'EDUCATION', 'Schools, education facilities, infrastructure', 'school', '#FF9800', 6),
('Agriculture Department', 'AGRICULTURE', 'Farming, irrigation, agricultural development', 'agriculture', '#8BC34A', 7),
('Roads Department', 'ROADS', 'Road maintenance, traffic, street lights', 'alt_route', '#607D8B', 8),
('Sanitation Department', 'SAN', 'Garbage collection, cleanliness, public toilets', 'cleaning_services', '#00BCD4', 9),
('Forest Department', 'FOREST', 'Forest conservation, wildlife, environment', 'forest', '#4CAF50', 10),
('Police Department', 'POLICE', 'Law and order, public safety', 'local_police', '#F44336', 11),
('Fire & Emergency', 'FIRE', 'Fire safety, emergency response', 'local_fire_department', '#E91E63', 12),
('Urban Development', 'URBAN', 'Urban planning, development projects', 'location_city', '#3F51B5', 13),
('Rural Development', 'RURAL', 'Rural infrastructure, MGNREGA', 'home_work', '#795548', 14),
('Social Welfare', 'WELFARE', 'Social programs, welfare schemes', 'volunteer_activism', '#9C27B0', 15)
ON CONFLICT (code) DO NOTHING;

-- Step 3: Add new columns to departments table
ALTER TABLE departments 
ADD COLUMN IF NOT EXISTS department_type_id UUID,
ADD COLUMN IF NOT EXISTS head_officer_id UUID,
ADD COLUMN IF NOT EXISTS office_address TEXT,
ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true;

-- Step 4: Create foreign keys
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'fk_departments_type'
    ) THEN
        ALTER TABLE departments
        ADD CONSTRAINT fk_departments_type 
            FOREIGN KEY (department_type_id) 
            REFERENCES department_types(id);
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'fk_departments_head_officer'
    ) THEN
        ALTER TABLE departments
        ADD CONSTRAINT fk_departments_head_officer 
            FOREIGN KEY (head_officer_id) 
            REFERENCES users(id);
    END IF;
END $$;

-- Step 5: Create indexes
CREATE INDEX IF NOT EXISTS ix_departments_type_id ON departments(department_type_id);
CREATE INDEX IF NOT EXISTS ix_departments_head_officer_id ON departments(head_officer_id);
CREATE INDEX IF NOT EXISTS ix_departments_is_active ON departments(is_active);

-- Step 6: Migrate existing departments to link with department types
-- Map existing departments to their types based on code
UPDATE departments d
SET department_type_id = (
    SELECT dt.id 
    FROM department_types dt 
    WHERE dt.code = d.code
    LIMIT 1
)
WHERE d.department_type_id IS NULL AND d.code IS NOT NULL;

-- Handle special cases where code doesn't match exactly
UPDATE departments d
SET department_type_id = (SELECT id FROM department_types WHERE code = 'WATER')
WHERE d.code IN ('WS', 'WATER_SUPPLY') AND d.department_type_id IS NULL;

UPDATE departments d
SET department_type_id = (SELECT id FROM department_types WHERE code = 'SAN')
WHERE d.code IN ('SANITATION', 'GARBAGE') AND d.department_type_id IS NULL;

-- Step 7: Assign department heads from existing department officers
-- Find the first department officer for each department and assign as head
UPDATE departments d
SET head_officer_id = (
    SELECT u.id 
    FROM users u 
    WHERE u.department_id = d.id 
      AND u.role = 'department_officer'
    ORDER BY u.created_at ASC
    LIMIT 1
)
WHERE d.head_officer_id IS NULL;

-- Step 8: Set all existing departments as active
UPDATE departments SET is_active = true WHERE is_active IS NULL;

-- Step 9: Add sample office addresses for existing departments
UPDATE departments d
SET office_address = CONCAT(d.name, ' Office, ', c.name, ', Karnataka')
FROM constituencies c
WHERE d.constituency_id = c.id AND d.office_address IS NULL;

-- Summary query
SELECT 
    '=== MIGRATION SUMMARY ===' as info;

SELECT 
    'Department Types Created' as metric,
    COUNT(*) as count
FROM department_types;

SELECT 
    'Departments Linked to Types' as metric,
    COUNT(*) as count
FROM departments 
WHERE department_type_id IS NOT NULL;

SELECT 
    'Departments with Heads Assigned' as metric,
    COUNT(*) as count
FROM departments 
WHERE head_officer_id IS NOT NULL;

SELECT 
    'Active Departments' as metric,
    COUNT(*) as count
FROM departments 
WHERE is_active = true;

-- Show department type distribution
SELECT 
    '=== DEPARTMENT TYPE DISTRIBUTION ===' as info;

SELECT 
    dt.name as department_type,
    dt.code,
    COUNT(d.id) as instance_count
FROM department_types dt
LEFT JOIN departments d ON d.department_type_id = dt.id
GROUP BY dt.id, dt.name, dt.code
ORDER BY instance_count DESC, dt.display_order;

-- Show sample departments with heads
SELECT 
    '=== SAMPLE DEPARTMENTS WITH HEADS ===' as info;

SELECT 
    d.name as department_name,
    dt.name as type,
    u.name as head_officer,
    u.phone as head_phone,
    d.office_address
FROM departments d
JOIN department_types dt ON d.department_type_id = dt.id
LEFT JOIN users u ON d.head_officer_id = u.id
LIMIT 10;
