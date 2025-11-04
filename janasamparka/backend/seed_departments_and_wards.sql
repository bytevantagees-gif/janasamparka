-- =====================================================
-- Seed Script: Departments with Jurisdiction & Ward Linking
-- =====================================================
-- Purpose: Create departments at different jurisdiction levels
--          Link wards to their parent panchayats
--          Create ward officers for testing
-- =====================================================

-- Get constituency IDs for reference
-- Puttur Constituency: 4eb94d2e-8ec5-48e8-b151-1928c5cad78b
-- Bantwal Constituency: 6a1e3a9a-c789-46fc-b807-240d619f2247
-- Mangalore City South: 9abec375-d9ca-41ba-ae02-3b94911db358

-- Get Puttur TP ID: 4760761a-74de-4a75-b7d7-8c28d39df3b8
-- Get Bantwal TP ID: ece20f0a-057a-4ba0-9020-6d6ecdce20f5

-- =====================================================
-- STEP 1: Create Departments with Jurisdiction
-- =====================================================

-- 1.1 TALUK PANCHAYAT LEVEL DEPARTMENTS (Puttur TP)
-- These departments serve all wards under Puttur Taluk Panchayat

INSERT INTO departments (id, name, code, constituency_id, taluk_panchayat_id, description, contact_phone, contact_email, created_at, updated_at)
VALUES
  (gen_random_uuid(), 'Puttur Public Works Department', 'PWD', '4eb94d2e-8ec5-48e8-b151-1928c5cad78b', '4760761a-74de-4a75-b7d7-8c28d39df3b8', 
   'Handles road construction, building maintenance, and infrastructure projects in Puttur TP area',
   '+91-8251-234567', 'puttur.pwd@karnataka.gov.in', NOW(), NOW()),
   
  (gen_random_uuid(), 'Puttur Electricity Department', 'ELEC', '4eb94d2e-8ec5-48e8-b151-1928c5cad78b', '4760761a-74de-4a75-b7d7-8c28d39df3b8',
   'Power supply issues, street lighting, transformer maintenance for Puttur TP',
   '+91-8251-234568', 'puttur.electricity@karnataka.gov.in', NOW(), NOW()),
   
  (gen_random_uuid(), 'Puttur Water Supply & Drainage', 'WATER', '4eb94d2e-8ec5-48e8-b151-1928c5cad78b', '4760761a-74de-4a75-b7d7-8c28d39df3b8',
   'Water supply, sewage, drainage systems in Puttur TP jurisdiction',
   '+91-8251-234569', 'puttur.water@karnataka.gov.in', NOW(), NOW()),
   
  (gen_random_uuid(), 'Puttur Health & Sanitation', 'HEALTH', '4eb94d2e-8ec5-48e8-b151-1928c5cad78b', '4760761a-74de-4a75-b7d7-8c28d39df3b8',
   'Primary health centers, sanitation, waste management in Puttur TP',
   '+91-8251-234570', 'puttur.health@karnataka.gov.in', NOW(), NOW()),
   
  (gen_random_uuid(), 'Puttur Revenue & Administration', 'REVENUE', '4eb94d2e-8ec5-48e8-b151-1928c5cad78b', '4760761a-74de-4a75-b7d7-8c28d39df3b8',
   'Land records, property tax, certificates in Puttur TP',
   '+91-8251-234571', 'puttur.revenue@karnataka.gov.in', NOW(), NOW());

-- 1.2 TALUK PANCHAYAT LEVEL DEPARTMENTS (Bantwal TP)
-- These departments serve Bantwal Taluk Panchayat area

INSERT INTO departments (id, name, code, constituency_id, taluk_panchayat_id, description, contact_phone, contact_email, created_at, updated_at)
VALUES
  (gen_random_uuid(), 'Bantwal Public Works Department', 'PWD', '6a1e3a9a-c789-46fc-b807-240d619f2247', 'ece20f0a-057a-4ba0-9020-6d6ecdce20f5',
   'Road and infrastructure maintenance for Bantwal TP',
   '+91-8255-234567', 'bantwal.pwd@karnataka.gov.in', NOW(), NOW()),
   
  (gen_random_uuid(), 'Bantwal Electricity Department', 'ELEC', '6a1e3a9a-c789-46fc-b807-240d619f2247', 'ece20f0a-057a-4ba0-9020-6d6ecdce20f5',
   'Power supply and street lighting for Bantwal TP',
   '+91-8255-234568', 'bantwal.electricity@karnataka.gov.in', NOW(), NOW()),
   
  (gen_random_uuid(), 'Bantwal Water Supply & Drainage', 'WATER', '6a1e3a9a-c789-46fc-b807-240d619f2247', 'ece20f0a-057a-4ba0-9020-6d6ecdce20f5',
   'Water and drainage systems for Bantwal TP',
   '+91-8255-234569', 'bantwal.water@karnataka.gov.in', NOW(), NOW());

-- 1.3 GRAM PANCHAYAT LEVEL DEPARTMENTS
-- Get GP ID for Panemangalore: 2f065e3e-9f3e-40d6-b311-75f3ea611a71

INSERT INTO departments (id, name, code, constituency_id, gram_panchayat_id, description, contact_phone, contact_email, created_at, updated_at)
VALUES
  (gen_random_uuid(), 'Panemangalore GP Public Works', 'PWD', '6a1e3a9a-c789-46fc-b807-240d619f2247', '2f065e3e-9f3e-40d6-b311-75f3ea611a71',
   'Village roads and infrastructure in Panemangalore Gram Panchayat',
   '+91-9876543210', 'panemangalore.pwd@karnataka.gov.in', NOW(), NOW()),
   
  (gen_random_uuid(), 'Panemangalore GP Water Supply', 'WATER', '6a1e3a9a-c789-46fc-b807-240d619f2247', '2f065e3e-9f3e-40d6-b311-75f3ea611a71',
   'Village water supply and sanitation in Panemangalore GP',
   '+91-9876543211', 'panemangalore.water@karnataka.gov.in', NOW(), NOW());

-- 1.4 CITY CORPORATION LEVEL DEPARTMENTS (Mangalore - when created)
-- Note: These will be added once city_corporations table is created
-- For now, we can use constituency_id to simulate Mangalore urban departments

-- Uncomment when city_corporations table is ready:
-- INSERT INTO departments (id, name, code, constituency_id, city_corporation_id, description, contact_phone, contact_email, created_at, updated_at)
-- VALUES
--   (gen_random_uuid(), 'Mangalore City Corporation PWD', 'PWD', '9abec375-d9ca-41ba-ae02-3b94911db358', '<mangalore_corp_id>',
--    'Urban infrastructure maintenance in Mangalore City',
--    '+91-824-2234567', 'mangalore.pwd@karnataka.gov.in', NOW(), NOW());

-- =====================================================
-- STEP 2: Link Wards to Parent Panchayats
-- =====================================================

-- 2.1 Link first 5 wards to Puttur Taluk Panchayat
-- Puttur TP ID: 4760761a-74de-4a75-b7d7-8c28d39df3b8

UPDATE wards
SET 
  ward_type = 'taluk_panchayat',
  taluk_panchayat_id = '4760761a-74de-4a75-b7d7-8c28d39df3b8',
  updated_at = NOW()
WHERE constituency_id = '4eb94d2e-8ec5-48e8-b151-1928c5cad78b'
  AND ward_number IN (1, 2, 3, 4, 5);

-- 2.2 Link wards 6-10 to another TP or GP (example: Bantwal TP)
-- Bantwal TP ID: ece20f0a-057a-4ba0-9020-6d6ecdce20f5

UPDATE wards
SET
  ward_type = 'taluk_panchayat',
  taluk_panchayat_id = 'ece20f0a-057a-4ba0-9020-6d6ecdce20f5',
  updated_at = NOW()
WHERE constituency_id = '6a1e3a9a-c789-46fc-b807-240d619f2247'
  AND ward_number IN (1, 2, 3);

-- 2.3 Link a ward to Gram Panchayat (Panemangalore GP)
-- Panemangalore GP ID: 2f065e3e-9f3e-40d6-b311-75f3ea611a71

UPDATE wards
SET
  ward_type = 'gram_panchayat',
  gram_panchayat_id = '2f065e3e-9f3e-40d6-b311-75f3ea611a71',
  updated_at = NOW()
WHERE constituency_id = '6a1e3a9a-c789-46fc-b807-240d619f2247'
  AND ward_number = 4;

-- =====================================================
-- STEP 3: Create Ward Officers (Users)
-- =====================================================

-- 3.1 Ward Officer for Puttur TP Ward 1
-- Ward 1 ID: 532ce9c5-ed09-49ec-9bb0-6dd5c92193df

INSERT INTO users (id, name, phone, password_hash, role, constituency_id, ward_id, created_at, updated_at, is_active)
VALUES
  (gen_random_uuid(), 'Ramesh Kumar', '+919876543210', 
   '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5vc6kGcL1UBhi',  -- password: 'Ward@123'
   'ward_officer', '4eb94d2e-8ec5-48e8-b151-1928c5cad78b', '532ce9c5-ed09-49ec-9bb0-6dd5c92193df',
   NOW(), NOW(), true);

-- 3.2 Ward Officer for Puttur TP Ward 2
-- Ward 2 ID: a053b761-a922-4548-97d1-1611a4a3b1f0

INSERT INTO users (id, name, phone, password_hash, role, constituency_id, ward_id, created_at, updated_at, is_active)
VALUES
  (gen_random_uuid(), 'Lakshmi Shenoy', '+919876543211',
   '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5vc6kGcL1UBhi',  -- password: 'Ward@123'
   'ward_officer', '4eb94d2e-8ec5-48e8-b151-1928c5cad78b', 'a053b761-a922-4548-97d1-1611a4a3b1f0',
   NOW(), NOW(), true);

-- 3.3 Ward Officer for Puttur TP Ward 3
-- Ward 3 ID: 6d3eab8f-ef9f-445e-a7ae-75d9a1290dcf

INSERT INTO users (id, name, phone, password_hash, role, constituency_id, ward_id, created_at, updated_at, is_active)
VALUES
  (gen_random_uuid(), 'Suresh Rao', '+919876543212',
   '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5vc6kGcL1UBhi',  -- password: 'Ward@123'
   'ward_officer', '4eb94d2e-8ec5-48e8-b151-1928c5cad78b', '6d3eab8f-ef9f-445e-a7ae-75d9a1290dcf',
   NOW(), NOW(), true);

-- =====================================================
-- STEP 4: Create Department Officers (Users)
-- =====================================================

-- 4.1 Get department IDs (need to query after insert)
-- We'll use a DO block to handle this properly

DO $$
DECLARE
  puttur_pwd_id UUID;
  puttur_elec_id UUID;
  puttur_water_id UUID;
  bantwal_pwd_id UUID;
BEGIN
  -- Get Puttur PWD department ID
  SELECT id INTO puttur_pwd_id FROM departments 
  WHERE name = 'Puttur Public Works Department' LIMIT 1;
  
  -- Get Puttur Electricity department ID
  SELECT id INTO puttur_elec_id FROM departments 
  WHERE name = 'Puttur Electricity Department' LIMIT 1;
  
  -- Get Puttur Water department ID
  SELECT id INTO puttur_water_id FROM departments 
  WHERE name = 'Puttur Water Supply & Drainage' LIMIT 1;
  
  -- Get Bantwal PWD department ID
  SELECT id INTO bantwal_pwd_id FROM departments 
  WHERE name = 'Bantwal Public Works Department' LIMIT 1;
  
  -- Create Department Officers for Puttur PWD
  IF puttur_pwd_id IS NOT NULL THEN
    INSERT INTO users (id, name, phone, password_hash, role, constituency_id, department_id, created_at, updated_at, is_active)
    VALUES
      (gen_random_uuid(), 'Prakash Bhat (PWD Head)', '+919876543220',
       '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5vc6kGcL1UBhi',  -- password: 'Ward@123'
       'department_officer', '4eb94d2e-8ec5-48e8-b151-1928c5cad78b', puttur_pwd_id,
       NOW(), NOW(), true),
       
      (gen_random_uuid(), 'Anita Kulkarni (PWD Engineer)', '+919876543221',
       '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5vc6kGcL1UBhi',
       'department_officer', '4eb94d2e-8ec5-48e8-b151-1928c5cad78b', puttur_pwd_id,
       NOW(), NOW(), true);
  END IF;
  
  -- Create Department Officer for Puttur Electricity
  IF puttur_elec_id IS NOT NULL THEN
    INSERT INTO users (id, name, phone, password_hash, role, constituency_id, department_id, created_at, updated_at, is_active)
    VALUES
      (gen_random_uuid(), 'Vinay Shetty (Electricity)', '+919876543222',
       '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5vc6kGcL1UBhi',
       'department_officer', '4eb94d2e-8ec5-48e8-b151-1928c5cad78b', puttur_elec_id,
       NOW(), NOW(), true);
  END IF;
  
  -- Create Department Officer for Puttur Water
  IF puttur_water_id IS NOT NULL THEN
    INSERT INTO users (id, name, phone, password_hash, role, constituency_id, department_id, created_at, updated_at, is_active)
    VALUES
      (gen_random_uuid(), 'Sunita Nayak (Water Supply)', '+919876543223',
       '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5vc6kGcL1UBhi',
       'department_officer', '4eb94d2e-8ec5-48e8-b151-1928c5cad78b', puttur_water_id,
       NOW(), NOW(), true);
  END IF;
  
  -- Create Department Officer for Bantwal PWD
  IF bantwal_pwd_id IS NOT NULL THEN
    INSERT INTO users (id, name, phone, password_hash, role, constituency_id, department_id, created_at, updated_at, is_active)
    VALUES
      (gen_random_uuid(), 'Mohan Acharya (Bantwal PWD)', '+919876543224',
       '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5vc6kGcL1UBhi',
       'department_officer', '6a1e3a9a-c789-46fc-b807-240d619f2247', bantwal_pwd_id,
       NOW(), NOW(), true);
  END IF;
END $$;

-- =====================================================
-- STEP 5: Verification Queries
-- =====================================================

-- Verify departments created
SELECT 
  d.name,
  d.code,
  CASE 
    WHEN d.gram_panchayat_id IS NOT NULL THEN 'Gram Panchayat Level'
    WHEN d.taluk_panchayat_id IS NOT NULL THEN 'Taluk Panchayat Level'
    WHEN d.zilla_panchayat_id IS NOT NULL THEN 'Zilla Panchayat Level'
    WHEN d.city_corporation_id IS NOT NULL THEN 'City Corporation Level'
    ELSE 'No Jurisdiction'
  END as jurisdiction_level,
  COALESCE(gp.name, tp.name, zp.name, 'N/A') as parent_body_name
FROM departments d
LEFT JOIN gram_panchayats gp ON d.gram_panchayat_id = gp.id
LEFT JOIN taluk_panchayats tp ON d.taluk_panchayat_id = tp.id
LEFT JOIN zilla_panchayats zp ON d.zilla_panchayat_id = zp.id
ORDER BY jurisdiction_level, d.name;

-- Verify wards linked to panchayats
SELECT 
  w.name as ward_name,
  w.ward_number,
  w.ward_type,
  COALESCE(gp.name, tp.name, 'Not Linked') as parent_body
FROM wards w
LEFT JOIN gram_panchayats gp ON w.gram_panchayat_id = gp.id
LEFT JOIN taluk_panchayats tp ON w.taluk_panchayat_id = tp.id
WHERE w.ward_type IS NOT NULL
ORDER BY w.ward_number;

-- Verify ward officers created
SELECT 
  u.name as officer_name,
  u.phone,
  w.name as assigned_ward,
  w.ward_number
FROM users u
JOIN wards w ON u.ward_id = w.id
WHERE u.role = 'ward_officer'
ORDER BY w.ward_number;

-- Verify department officers created
SELECT 
  u.name as officer_name,
  u.phone,
  d.name as department,
  d.code
FROM users u
JOIN departments d ON u.department_id = d.id
WHERE u.role = 'department_officer'
ORDER BY d.name;

-- =====================================================
-- SUMMARY
-- =====================================================
-- Created:
-- - 10 Departments (5 Puttur TP, 3 Bantwal TP, 2 Panemangalore GP)
-- - Linked 9 wards to parent panchayats
-- - Created 3 ward officers
-- - Created 5 department officers
-- 
-- Test Credentials:
-- Phone: +919876543210 to +919876543224
-- Password: Ward@123
-- =====================================================
