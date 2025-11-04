-- Karnataka Governance Hierarchy - Complete Schema Migration
-- Phase 1: Create proper administrative structure

-- ============================================
-- 1. CREATE CITY CORPORATIONS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS city_corporations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) NOT NULL UNIQUE,
    
    -- Hierarchy
    constituency_id UUID NOT NULL REFERENCES constituencies(id),
    zilla_panchayat_id UUID REFERENCES zilla_panchayats(id),
    
    -- Location
    district VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL DEFAULT 'Karnataka',
    
    -- Stats
    total_wards INTEGER NOT NULL DEFAULT 0,
    total_population INTEGER NOT NULL DEFAULT 0,
    area_sq_km DECIMAL(10, 2),
    
    -- Leadership
    mayor_name VARCHAR(255),
    deputy_mayor_name VARCHAR(255),
    commissioner_name VARCHAR(255),
    
    -- Contact
    office_phone VARCHAR(20),
    office_email VARCHAR(255),
    office_address TEXT,
    
    -- Metadata
    is_active BOOLEAN NOT NULL DEFAULT true,
    tier VARCHAR(10) CHECK (tier IN ('tier-1', 'tier-2', 'tier-3')),
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_city_corporations_constituency ON city_corporations(constituency_id);
CREATE INDEX idx_city_corporations_zilla ON city_corporations(zilla_panchayat_id);
CREATE INDEX idx_city_corporations_active ON city_corporations(is_active);

-- ============================================
-- 2. CREATE TOWN MUNICIPALITIES TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS town_municipalities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) NOT NULL UNIQUE,
    
    -- Hierarchy (Town Municipalities are within Taluks)
    constituency_id UUID NOT NULL REFERENCES constituencies(id),
    taluk_panchayat_id UUID NOT NULL REFERENCES taluk_panchayats(id),
    zilla_panchayat_id UUID REFERENCES zilla_panchayats(id),
    
    -- Location
    taluk_name VARCHAR(100) NOT NULL,
    district VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL DEFAULT 'Karnataka',
    
    -- Stats
    total_wards INTEGER NOT NULL DEFAULT 0,
    total_population INTEGER NOT NULL DEFAULT 0,
    area_sq_km DECIMAL(10, 2),
    
    -- Leadership
    president_name VARCHAR(255),
    vice_president_name VARCHAR(255),
    chief_officer_name VARCHAR(255),
    
    -- Contact
    office_phone VARCHAR(20),
    office_email VARCHAR(255),
    office_address TEXT,
    
    -- Metadata
    is_active BOOLEAN NOT NULL DEFAULT true,
    municipality_class VARCHAR(20) CHECK (municipality_class IN ('Class-I', 'Class-II', 'Class-III')),
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_town_muni_constituency ON town_municipalities(constituency_id);
CREATE INDEX idx_town_muni_taluk ON town_municipalities(taluk_panchayat_id);
CREATE INDEX idx_town_muni_zilla ON town_municipalities(zilla_panchayat_id);
CREATE INDEX idx_town_muni_active ON town_municipalities(is_active);

-- ============================================
-- 3. UPDATE WARDS TABLE
-- ============================================

-- Add town_municipality_id
ALTER TABLE wards ADD COLUMN IF NOT EXISTS town_municipality_id UUID REFERENCES town_municipalities(id);
CREATE INDEX IF NOT EXISTS idx_wards_town_municipality ON wards(town_municipality_id);

-- Add ward officer and member fields
ALTER TABLE wards ADD COLUMN IF NOT EXISTS ward_officer_id UUID REFERENCES users(id);
ALTER TABLE wards ADD COLUMN IF NOT EXISTS ward_member_name VARCHAR(255);
ALTER TABLE wards ADD COLUMN IF NOT EXISTS ward_member_phone VARCHAR(20);
ALTER TABLE wards ADD COLUMN IF NOT EXISTS ward_member_party VARCHAR(100);

-- Update city_corporation_id to reference the new table
ALTER TABLE wards DROP CONSTRAINT IF EXISTS wards_city_corporation_id_fkey;
ALTER TABLE wards ADD CONSTRAINT wards_city_corporation_id_fkey 
    FOREIGN KEY (city_corporation_id) REFERENCES city_corporations(id);

-- ============================================
-- 4. UPDATE DEPARTMENTS TABLE
-- ============================================

-- Add town_municipality_id
ALTER TABLE departments ADD COLUMN IF NOT EXISTS town_municipality_id UUID REFERENCES town_municipalities(id);
CREATE INDEX IF NOT EXISTS idx_departments_town_municipality ON departments(town_municipality_id);

-- Add administrative level
ALTER TABLE departments ADD COLUMN IF NOT EXISTS administrative_level VARCHAR(30) 
    CHECK (administrative_level IN ('state', 'zilla', 'taluk', 'gram_panchayat', 'town_municipality', 'city_corporation', 'constituency'));

-- ============================================
-- 5. UPDATE COMPLAINTS TABLE
-- ============================================

-- Add town_municipality and city_corporation
ALTER TABLE complaints ADD COLUMN IF NOT EXISTS town_municipality_id UUID REFERENCES town_municipalities(id);
ALTER TABLE complaints DROP CONSTRAINT IF EXISTS complaints_city_corporation_id_fkey;
ALTER TABLE complaints ADD COLUMN IF NOT EXISTS city_corporation_id UUID REFERENCES city_corporations(id);

CREATE INDEX IF NOT EXISTS idx_complaints_town_municipality ON complaints(town_municipality_id);
CREATE INDEX IF NOT EXISTS idx_complaints_city_corporation ON complaints(city_corporation_id);

-- Add assignment hierarchy tracking
ALTER TABLE complaints ADD COLUMN IF NOT EXISTS assigned_entity_type VARCHAR(30)
    CHECK (assigned_entity_type IN ('ward', 'gram_panchayat', 'taluk_panchayat', 'town_municipality', 'city_corporation', 'zilla_panchayat', 'department'));
ALTER TABLE complaints ADD COLUMN IF NOT EXISTS assigned_entity_id UUID;
ALTER TABLE complaints ADD COLUMN IF NOT EXISTS escalation_level INTEGER DEFAULT 0;
ALTER TABLE complaints ADD COLUMN IF NOT EXISTS can_escalate_to VARCHAR(30);

-- ============================================
-- 6. CREATE ADMINISTRATIVE HIERARCHY VIEW
-- ============================================

DROP VIEW IF EXISTS administrative_hierarchy CASCADE;

CREATE OR REPLACE VIEW administrative_hierarchy AS
SELECT 
    'zilla_panchayat' as entity_type,
    zp.id as entity_id,
    zp.name as entity_name,
    NULL::uuid as parent_id,
    'district' as level,
    zp.constituency_id,
    zp.district,
    zp.total_population as population,
    zp.is_active
FROM zilla_panchayats zp

UNION ALL

SELECT 
    'taluk_panchayat',
    tp.id,
    tp.name,
    tp.zilla_panchayat_id,
    'taluk',
    tp.constituency_id,
    tp.district,
    tp.total_population,
    tp.is_active
FROM taluk_panchayats tp

UNION ALL

SELECT 
    'gram_panchayat',
    gp.id,
    gp.name,
    gp.taluk_panchayat_id,
    'village',
    gp.constituency_id,
    gp.district,
    gp.population,
    gp.is_active
FROM gram_panchayats gp

UNION ALL

SELECT 
    'town_municipality',
    tm.id,
    tm.name,
    tm.taluk_panchayat_id,
    'town',
    tm.constituency_id,
    tm.district,
    tm.total_population,
    tm.is_active
FROM town_municipalities tm

UNION ALL

SELECT 
    'city_corporation',
    cc.id,
    cc.name,
    cc.zilla_panchayat_id,
    'city',
    cc.constituency_id,
    cc.district,
    cc.total_population,
    cc.is_active
FROM city_corporations cc;

-- ============================================
-- PHASE 2: SEED DATA
-- ============================================

-- Get constituency and zilla IDs (we'll use existing ones)
DO $$
DECLARE
    dk_constituency_id UUID;
    udupi_constituency_id UUID;
    uttara_kannada_constituency_id UUID;
    dk_zilla_id UUID;
BEGIN
    -- Get Dakshina Kannada constituency
    SELECT id INTO dk_constituency_id FROM constituencies WHERE name LIKE '%Dakshina%' OR name LIKE '%Puttur%' LIMIT 1;
    IF dk_constituency_id IS NULL THEN
        SELECT id INTO dk_constituency_id FROM constituencies LIMIT 1;
    END IF;

    -- Get Udupi constituency
    SELECT id INTO udupi_constituency_id FROM constituencies WHERE name LIKE '%Udupi%' LIMIT 1;
    IF udupi_constituency_id IS NULL THEN
        SELECT id INTO udupi_constituency_id FROM constituencies OFFSET 1 LIMIT 1;
    END IF;

    -- Get Uttara Kannada constituency
    SELECT id INTO uttara_kannada_constituency_id FROM constituencies WHERE name LIKE '%Uttara%' OR name LIKE '%Karwar%' LIMIT 1;
    IF uttara_kannada_constituency_id IS NULL THEN
        SELECT id INTO uttara_kannada_constituency_id FROM constituencies OFFSET 2 LIMIT 1;
    END IF;

    -- Get or create Dakshina Kannada Zilla Panchayat
    SELECT id INTO dk_zilla_id FROM zilla_panchayats WHERE district = 'Dakshina Kannada' LIMIT 1;
    IF dk_zilla_id IS NULL THEN
        INSERT INTO zilla_panchayats (
            name, code, district, state,
            total_taluk_panchayats, total_gram_panchayats, total_population,
            president_name, chief_executive_officer_name,
            office_phone, office_email, office_address,
            is_active, description
        ) VALUES (
            'Dakshina Kannada Zilla Panchayat',
            'DK_ZP_001',
            'Dakshina Kannada',
            'Karnataka',
            5, 25, 2089649,
            'Smt. Meenakshi Shanthigodu',
            'Sri. K.V. Rajendra',
            '+91824-2220123',
            'ceo.dk@karnataka.gov.in',
            'Zilla Panchayat Office, Mangalore, Dakshina Kannada - 575001',
            true,
            'Zilla Panchayat for Dakshina Kannada District'
        ) RETURNING id INTO dk_zilla_id;
    END IF;

    -- Create Mangalore City Corporation
    INSERT INTO city_corporations (
        name, code, constituency_id, zilla_panchayat_id,
        district, state, total_wards, total_population, area_sq_km,
        mayor_name, deputy_mayor_name, commissioner_name,
        office_phone, office_email, office_address,
        tier, is_active, description
    ) VALUES (
        'Mangalore City Corporation',
        'MCC_001',
        dk_constituency_id,
        dk_zilla_id,
        'Dakshina Kannada',
        'Karnataka',
        60,
        488968,
        170.00,
        'Smt. Premananda Shetty',
        'Sri. Shakeeb Ahmad',
        'Sri. Akshy Sridhar IAS',
        '+91824-2441216',
        'commissioner@mangalurecity.mrc.gov.in',
        'Mangalore City Corporation, Lalbagh, Mangalore - 575001',
        'tier-2',
        true,
        'Municipal Corporation for Mangalore City'
    ) ON CONFLICT (code) DO NOTHING;

    -- Create Udupi City Municipality
    INSERT INTO city_corporations (
        name, code, constituency_id, zilla_panchayat_id,
        district, state, total_wards, total_population, area_sq_km,
        mayor_name, commissioner_name,
        office_phone, office_email, office_address,
        tier, is_active, description
    ) VALUES (
        'Udupi City Municipality',
        'UDU_MUN_001',
        udupi_constituency_id,
        NULL,
        'Udupi',
        'Karnataka',
        35,
        181877,
        55.00,
        'Sri. Sumitra Nayak',
        'Smt. Ananthapadmanabha M',
        '+91820-2529777',
        'commissioner@udupicity.gov.in',
        'City Municipality Office, Udupi - 576101',
        'tier-3',
        true,
        'City Municipality for Udupi'
    ) ON CONFLICT (code) DO NOTHING;

    -- Create Karwar Town Municipality
    INSERT INTO city_corporations (
        name, code, constituency_id, zilla_panchayat_id,
        district, state, total_wards, total_population, area_sq_km,
        mayor_name, commissioner_name,
        office_phone, office_email, office_address,
        tier, is_active, description
    ) VALUES (
        'Karwar Town Municipality',
        'KAR_MUN_001',
        uttara_kannada_constituency_id,
        NULL,
        'Uttara Kannada',
        'Karnataka',
        23,
        81725,
        35.00,
        'Sri. Ashok Naik',
        'Smt. Priya Kumar',
        '+91838-2226633',
        'commissioner@karwartown.gov.in',
        'Town Municipality Office, Karwar - 581301',
        'tier-3',
        true,
        'Town Municipality for Karwar'
    ) ON CONFLICT (code) DO NOTHING;

    RAISE NOTICE 'City Corporations created successfully';

END $$;

-- Update existing city_corporation wards to link to Mangalore City Corporation
UPDATE wards 
SET city_corporation_id = (SELECT id FROM city_corporations WHERE code = 'MCC_001' LIMIT 1),
    updated_at = NOW()
WHERE ward_type = 'city_corporation' 
  AND city_corporation_id IS NULL
  AND taluk LIKE '%Mangalore%';

-- Link wards from other areas
UPDATE wards 
SET city_corporation_id = (SELECT id FROM city_corporations WHERE code = 'UDU_MUN_001' LIMIT 1),
    updated_at = NOW()
WHERE ward_type = 'city_corporation' 
  AND city_corporation_id IS NULL
  AND (name LIKE '%Udupi%' OR taluk LIKE '%Udupi%');

UPDATE wards 
SET city_corporation_id = (SELECT id FROM city_corporations WHERE code = 'KAR_MUN_001' LIMIT 1),
    updated_at = NOW()
WHERE ward_type = 'city_corporation' 
  AND city_corporation_id IS NULL
  AND (name LIKE '%Karwar%' OR taluk LIKE '%Karwar%');

-- Link remaining city_corporation wards to Mangalore
UPDATE wards 
SET city_corporation_id = (SELECT id FROM city_corporations WHERE code = 'MCC_001' LIMIT 1),
    updated_at = NOW()
WHERE ward_type = 'city_corporation' AND city_corporation_id IS NULL;

-- Update city_corporations ward counts
UPDATE city_corporations cc
SET total_wards = (
    SELECT COUNT(*) FROM wards WHERE city_corporation_id = cc.id
),
updated_at = NOW();

-- Show results
SELECT 
    'City Corporations' as entity,
    COUNT(*) as count
FROM city_corporations
UNION ALL
SELECT 
    'Wards linked to Corporations',
    COUNT(*)
FROM wards WHERE city_corporation_id IS NOT NULL
UNION ALL
SELECT
    'Wards without parent',
    COUNT(*)
FROM wards WHERE gram_panchayat_id IS NULL 
  AND taluk_panchayat_id IS NULL 
  AND city_corporation_id IS NULL
  AND town_municipality_id IS NULL;
