-- =====================================================
-- Seed Script: Create Ward Officers and Department Officers
-- =====================================================
-- Note: This system uses Firebase authentication
-- Users will need to register via Firebase first
-- This script creates user records with phone numbers
-- =====================================================

-- =====================================================
-- STEP 1: Create Ward Officers
-- =====================================================

-- Ward Officer for Puttur TP Ward 1 (Kemminje)
INSERT INTO users (id, name, phone, role, constituency_id, ward_id, created_at, updated_at, is_active, locale_pref)
VALUES
  (gen_random_uuid(), 'Ramesh Kumar', '+919876543210',
   'ward_officer', '4eb94d2e-8ec5-48e8-b151-1928c5cad78b', '532ce9c5-ed09-49ec-9bb0-6dd5c92193df',
   NOW(), NOW(), 'true', 'kn');

-- Ward Officer for Puttur TP Ward 2 (Neria)
INSERT INTO users (id, name, phone, role, constituency_id, ward_id, created_at, updated_at, is_active, locale_pref)
VALUES
  (gen_random_uuid(), 'Lakshmi Shenoy', '+919876543211',
   'ward_officer', '4eb94d2e-8ec5-48e8-b151-1928c5cad78b', 'a053b761-a922-4548-97d1-1611a4a3b1f0',
   NOW(), NOW(), 'true', 'kn');

-- Ward Officer for Puttur TP Ward 3 (Kabaka)
INSERT INTO users (id, name, phone, role, constituency_id, ward_id, created_at, updated_at, is_active, locale_pref)
VALUES
  (gen_random_uuid(), 'Suresh Rao', '+919876543212',
   'ward_officer', '4eb94d2e-8ec5-48e8-b151-1928c5cad78b', '6d3eab8f-ef9f-445e-a7ae-75d9a1290dcf',
   NOW(), NOW(), 'true', 'kn');

-- =====================================================
-- STEP 2: Create Department Officers
-- =====================================================

-- Department Officers for Puttur PWD
DO $$
DECLARE
  puttur_pwd_id UUID;
  puttur_elec_id UUID;
  puttur_water_id UUID;
  bantwal_pwd_id UUID;
BEGIN
  -- Get department IDs
  SELECT id INTO puttur_pwd_id FROM departments 
  WHERE name = 'Puttur Public Works Department' LIMIT 1;
  
  SELECT id INTO puttur_elec_id FROM departments 
  WHERE name = 'Puttur Electricity Department' LIMIT 1;
  
  SELECT id INTO puttur_water_id FROM departments 
  WHERE name = 'Puttur Water Supply & Drainage' LIMIT 1;
  
  SELECT id INTO bantwal_pwd_id FROM departments 
  WHERE name = 'Bantwal Public Works Department' LIMIT 1;
  
  -- Create Department Officers for Puttur PWD
  IF puttur_pwd_id IS NOT NULL THEN
    INSERT INTO users (id, name, phone, role, constituency_id, department_id, created_at, updated_at, is_active, locale_pref)
    VALUES
      (gen_random_uuid(), 'Prakash Bhat (PWD Head)', '+919876543220',
       'department_officer', '4eb94d2e-8ec5-48e8-b151-1928c5cad78b', puttur_pwd_id,
       NOW(), NOW(), 'true', 'kn'),
       
      (gen_random_uuid(), 'Anita Kulkarni (PWD Engineer)', '+919876543221',
       'department_officer', '4eb94d2e-8ec5-48e8-b151-1928c5cad78b', puttur_pwd_id,
       NOW(), NOW(), 'true', 'kn');
  END IF;
  
  -- Create Department Officer for Puttur Electricity
  IF puttur_elec_id IS NOT NULL THEN
    INSERT INTO users (id, name, phone, role, constituency_id, department_id, created_at, updated_at, is_active, locale_pref)
    VALUES
      (gen_random_uuid(), 'Vinay Shetty (Electricity)', '+919876543222',
       'department_officer', '4eb94d2e-8ec5-48e8-b151-1928c5cad78b', puttur_elec_id,
       NOW(), NOW(), 'true', 'kn');
  END IF;
  
  -- Create Department Officer for Puttur Water
  IF puttur_water_id IS NOT NULL THEN
    INSERT INTO users (id, name, phone, role, constituency_id, department_id, created_at, updated_at, is_active, locale_pref)
    VALUES
      (gen_random_uuid(), 'Sunita Nayak (Water Supply)', '+919876543223',
       'department_officer', '4eb94d2e-8ec5-48e8-b151-1928c5cad78b', puttur_water_id,
       NOW(), NOW(), 'true', 'kn');
  END IF;
  
  -- Create Department Officer for Bantwal PWD
  IF bantwal_pwd_id IS NOT NULL THEN
    INSERT INTO users (id, name, phone, role, constituency_id, department_id, created_at, updated_at, is_active, locale_pref)
    VALUES
      (gen_random_uuid(), 'Mohan Acharya (Bantwal PWD)', '+919876543224',
       'department_officer', '6a1e3a9a-c789-46fc-b807-240d619f2247', bantwal_pwd_id,
       NOW(), NOW(), 'true', 'kn');
  END IF;
END $$;

-- =====================================================
-- STEP 3: Verification
-- =====================================================

-- Verify ward officers created
SELECT 
  u.name as officer_name,
  u.phone,
  w.name as assigned_ward,
  w.ward_number,
  w.ward_type,
  COALESCE(tp.name, gp.name) as parent_body
FROM users u
JOIN wards w ON u.ward_id = w.id
LEFT JOIN taluk_panchayats tp ON w.taluk_panchayat_id = tp.id
LEFT JOIN gram_panchayats gp ON w.gram_panchayat_id = gp.id
WHERE u.role = 'ward_officer'
ORDER BY w.ward_number;

-- Verify department officers created
SELECT 
  u.name as officer_name,
  u.phone,
  d.name as department,
  d.code,
  CASE 
    WHEN d.taluk_panchayat_id IS NOT NULL THEN 'Taluk Panchayat'
    WHEN d.gram_panchayat_id IS NOT NULL THEN 'Gram Panchayat'
    ELSE 'Other'
  END as dept_level
FROM users u
JOIN departments d ON u.department_id = d.id
WHERE u.role = 'department_officer'
ORDER BY d.name;

-- =====================================================
-- SUMMARY
-- =====================================================
-- Created:
-- - 3 Ward Officers (Puttur TP Wards 1, 2, 3)
-- - 5 Department Officers (PWD, Electricity, Water)
-- 
-- Note: These users need to register via Firebase with these phone numbers
-- Phone: +919876543210 to +919876543224
-- =====================================================
