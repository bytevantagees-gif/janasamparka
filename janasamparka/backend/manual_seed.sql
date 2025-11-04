-- Manual seed data for 3 constituencies
-- Run this: docker-compose exec db psql -U janasamparka -d janasamparka_db -f /path/to/this/file

BEGIN;

-- 1. Puttur Constituency
INSERT INTO constituencies (id, name, code, district, state, mla_name, mla_party, mla_contact_phone, assembly_number, total_wards, is_active, subscription_tier, created_at, updated_at)
VALUES (
  gen_random_uuid(),
  'Puttur',
  'PUT001',
  'Dakshina Kannada',
  'Karnataka',
  'Ashok Kumar Rai',
  'Indian National Congress',
  '+918242226666',
  172,
  35,
  true,
  'premium',
  NOW(),
  NOW()
) RETURNING id as puttur_id \gset

-- 2. Mangalore North Constituency
INSERT INTO constituencies (id, name, code, district, state, mla_name, mla_party, mla_contact_phone, assembly_number, total_wards, is_active, subscription_tier, created_at, updated_at)
VALUES (
  gen_random_uuid(),
  'Mangalore North',
  'MNG001',
  'Dakshina Kannada',
  'Karnataka',
  'B.A. Mohiuddin Bava',
  'Indian National Congress',
  '+918242227777',
  129,
  45,
  true,
  'premium',
  NOW(),
  NOW()
) RETURNING id as mangalore_id \gset

-- 3. Udupi Constituency
INSERT INTO constituencies (id, name, code, district, state, mla_name, mla_party, mla_contact_phone, assembly_number, total_wards, is_active, subscription_tier, created_at, updated_at)
VALUES (
  gen_random_uuid(),
  'Udupi',
  'UDU001',
  'Udupi',
  'Karnataka',
  'Yashpal A. Suvarna',
  'Bharatiya Janata Party',
  '+918252255555',
  156,
  40,
  true,
  'premium',
  NOW(),
  NOW()
) RETURNING id as udupi_id \gset

COMMIT;

-- Verify
SELECT name, code, mla_name FROM constituencies;
