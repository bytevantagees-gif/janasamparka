-- Migration: Add 3-Tier Panchayat Raj System
-- Description: Integrate Gram, Taluk, and Zilla Panchayats with roles (PDO, VA, etc.)
-- Date: 2024-10-30

-- ============================================
-- STEP 1: Create Zilla Panchayat (District Level)
-- ============================================

CREATE TABLE IF NOT EXISTS zilla_panchayats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Basic Info
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    
    -- Location
    district VARCHAR(100) NOT NULL UNIQUE,
    state VARCHAR(50) DEFAULT 'Karnataka',
    
    -- Demographics
    total_taluk_panchayats INTEGER DEFAULT 0,
    total_gram_panchayats INTEGER DEFAULT 0,
    total_population INTEGER DEFAULT 0,
    
    -- Administration
    president_name VARCHAR(255),
    chief_executive_officer_name VARCHAR(255),
    
    -- Contact
    office_phone VARCHAR(15),
    office_email VARCHAR(255),
    office_address TEXT,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Metadata
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_zilla_panchayats_district ON zilla_panchayats(district);
CREATE INDEX IF NOT EXISTS idx_zilla_panchayats_code ON zilla_panchayats(code);

-- ============================================
-- STEP 2: Create Taluk Panchayat (Block Level)
-- ============================================

CREATE TABLE IF NOT EXISTS taluk_panchayats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Basic Info
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    
    -- Hierarchy
    zilla_panchayat_id UUID REFERENCES zilla_panchayats(id),
    constituency_id UUID NOT NULL REFERENCES constituencies(id),
    
    -- Location
    taluk_name VARCHAR(100) NOT NULL,
    district VARCHAR(100) NOT NULL,
    state VARCHAR(50) DEFAULT 'Karnataka',
    
    -- Demographics
    total_gram_panchayats INTEGER DEFAULT 0,
    total_population INTEGER DEFAULT 0,
    
    -- Administration
    president_name VARCHAR(255),
    executive_officer_name VARCHAR(255),
    
    -- Contact
    office_phone VARCHAR(15),
    office_email VARCHAR(255),
    office_address TEXT,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Metadata
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_taluk_panchayats_constituency ON taluk_panchayats(constituency_id);
CREATE INDEX IF NOT EXISTS idx_taluk_panchayats_zilla ON taluk_panchayats(zilla_panchayat_id);
CREATE INDEX IF NOT EXISTS idx_taluk_panchayats_code ON taluk_panchayats(code);

-- ============================================
-- STEP 3: Create Gram Panchayat (Village Level)
-- ============================================

CREATE TABLE IF NOT EXISTS gram_panchayats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Basic Info
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    
    -- Hierarchy
    taluk_panchayat_id UUID REFERENCES taluk_panchayats(id),
    constituency_id UUID NOT NULL REFERENCES constituencies(id),
    
    -- Location
    taluk_name VARCHAR(100) NOT NULL,
    district VARCHAR(100) NOT NULL,
    state VARCHAR(50) DEFAULT 'Karnataka',
    
    -- Demographics
    population INTEGER DEFAULT 0,
    households INTEGER DEFAULT 0,
    villages_covered INTEGER DEFAULT 1,
    
    -- Administration
    president_name VARCHAR(255),
    vice_president_name VARCHAR(255),
    secretary_name VARCHAR(255),
    
    -- Contact
    office_phone VARCHAR(15),
    office_email VARCHAR(255),
    office_address TEXT,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Metadata
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_gram_panchayats_constituency ON gram_panchayats(constituency_id);
CREATE INDEX IF NOT EXISTS idx_gram_panchayats_taluk ON gram_panchayats(taluk_panchayat_id);
CREATE INDEX IF NOT EXISTS idx_gram_panchayats_code ON gram_panchayats(code);
CREATE INDEX IF NOT EXISTS idx_gram_panchayats_taluk_name ON gram_panchayats(taluk_name);

-- ============================================
-- STEP 4: Update Users Table with Panchayat Roles
-- ============================================

-- Add new panchayat role types to UserRole enum
-- Note: In PostgreSQL with enum, we need to alter the type
DO $$ 
BEGIN
    -- Add new roles if they don't exist
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'userrole') THEN
        -- Enum doesn't exist, will be created by SQLAlchemy
        NULL;
    ELSE
        -- Add new enum values (PostgreSQL 12+)
        ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'pdo';
        ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'village_accountant';
        ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'taluk_panchayat_officer';
        ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'zilla_panchayat_officer';
        ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'gp_president';
        ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'tp_president';
        ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'zp_president';
    END IF;
END $$;

-- Add panchayat foreign keys to users table
ALTER TABLE users
ADD COLUMN IF NOT EXISTS gram_panchayat_id UUID REFERENCES gram_panchayats(id);

ALTER TABLE users
ADD COLUMN IF NOT EXISTS taluk_panchayat_id UUID REFERENCES taluk_panchayats(id);

ALTER TABLE users
ADD COLUMN IF NOT EXISTS zilla_panchayat_id UUID REFERENCES zilla_panchayats(id);

-- Add indexes for panchayat assignments
CREATE INDEX IF NOT EXISTS idx_users_gram_panchayat ON users(gram_panchayat_id);
CREATE INDEX IF NOT EXISTS idx_users_taluk_panchayat ON users(taluk_panchayat_id);
CREATE INDEX IF NOT EXISTS idx_users_zilla_panchayat ON users(zilla_panchayat_id);

-- ============================================
-- STEP 5: Insert Sample Data - Dakshina Kannada District
-- ============================================

-- Insert Zilla Panchayat for Dakshina Kannada
INSERT INTO zilla_panchayats (id, name, code, district, total_taluk_panchayats, total_population, president_name, chief_executive_officer_name)
VALUES (
    gen_random_uuid(),
    'Dakshina Kannada Zilla Panchayat',
    'ZP-DK-001',
    'Dakshina Kannada',
    5,
    2100000,
    'Meenakshi Shanthigodu',
    'Dr. Kumar R. (CEO)'
) ON CONFLICT (code) DO NOTHING;

-- Get Zilla Panchayat ID
DO $$
DECLARE
    zp_id UUID;
    puttur_const_id UUID;
    mangalore_const_id UUID;
    tp_puttur_id UUID;
    tp_kadaba_id UUID;
BEGIN
    -- Get ZP ID
    SELECT id INTO zp_id FROM zilla_panchayats WHERE code = 'ZP-DK-001';
    
    -- Get Constituency IDs
    SELECT id INTO puttur_const_id FROM constituencies WHERE code = 'PUT001';
    SELECT id INTO mangalore_const_id FROM constituencies WHERE code = 'MNG001';

    -- Insert Taluk Panchayats
    INSERT INTO taluk_panchayats (id, name, code, zilla_panchayat_id, constituency_id, taluk_name, district, total_gram_panchayats, total_population, president_name, executive_officer_name)
    VALUES 
        (gen_random_uuid(), 'Puttur Taluk Panchayat', 'TP-PUT-001', zp_id, puttur_const_id, 'Puttur', 'Dakshina Kannada', 25, 145000, 'Rajesh Kumar', 'Suresh B.O.'),
        (gen_random_uuid(), 'Kadaba Taluk Panchayat', 'TP-KAD-001', zp_id, puttur_const_id, 'Kadaba', 'Dakshina Kannada', 18, 95000, 'Savitha Rao', 'Prakash M.')
    ON CONFLICT (code) DO NOTHING;

    -- Get Taluk Panchayat IDs
    SELECT id INTO tp_puttur_id FROM taluk_panchayats WHERE code = 'TP-PUT-001';
    SELECT id INTO tp_kadaba_id FROM taluk_panchayats WHERE code = 'TP-KAD-001';

    -- Insert Sample Gram Panchayats under Puttur Taluk
    INSERT INTO gram_panchayats (name, code, taluk_panchayat_id, constituency_id, taluk_name, district, population, households, villages_covered, president_name, secretary_name)
    VALUES 
        ('Bolwar Gram Panchayat', 'GP-PUT-001', tp_puttur_id, puttur_const_id, 'Puttur', 'Dakshina Kannada', 8500, 1800, 3, 'Manoj Shetty', 'Ramesh PDO'),
        ('Kabaka Gram Panchayat', 'GP-PUT-002', tp_puttur_id, puttur_const_id, 'Puttur', 'Dakshina Kannada', 6200, 1300, 2, 'Suma Bhat', 'Ganesh PDO'),
        ('Parladka Gram Panchayat', 'GP-PUT-003', tp_puttur_id, puttur_const_id, 'Puttur', 'Dakshina Kannada', 5800, 1200, 2, 'Krishna Rao', 'Mohan PDO')
    ON CONFLICT (code) DO NOTHING;

    -- Insert Sample Gram Panchayats under Kadaba Taluk
    INSERT INTO gram_panchayats (name, code, taluk_panchayat_id, constituency_id, taluk_name, district, population, households, villages_covered, president_name, secretary_name)
    VALUES 
        ('Nettanige Mudnur GP', 'GP-KAD-001', tp_kadaba_id, puttur_const_id, 'Kadaba', 'Dakshina Kannada', 7200, 1500, 3, 'Vasanth Kumar', 'Sunil PDO'),
        ('Kodimbala GP', 'GP-KAD-002', tp_kadaba_id, puttur_const_id, 'Kadaba', 'Dakshina Kannada', 5500, 1100, 2, 'Meena Shetty', 'Ravi PDO')
    ON CONFLICT (code) DO NOTHING;

END $$;

-- ============================================
-- STEP 6: Verify Installation
-- ============================================

-- Show hierarchy
SELECT 
    'Zilla Panchayats' as level,
    COUNT(*) as count
FROM zilla_panchayats
UNION ALL
SELECT 
    'Taluk Panchayats' as level,
    COUNT(*) as count
FROM taluk_panchayats
UNION ALL
SELECT 
    'Gram Panchayats' as level,
    COUNT(*) as count
FROM gram_panchayats;

-- Show Panchayat hierarchy for Puttur
SELECT 
    'ZP: ' || zp.name as hierarchy,
    zp.district,
    NULL as taluk,
    NULL as gram_panchayat
FROM zilla_panchayats zp
WHERE zp.district = 'Dakshina Kannada'
UNION ALL
SELECT 
    '  └─ TP: ' || tp.name as hierarchy,
    tp.district,
    tp.taluk_name as taluk,
    NULL as gram_panchayat
FROM taluk_panchayats tp
WHERE tp.district = 'Dakshina Kannada'
UNION ALL
SELECT 
    '      └─ GP: ' || gp.name as hierarchy,
    gp.district,
    gp.taluk_name as taluk,
    gp.name as gram_panchayat
FROM gram_panchayats gp
WHERE gp.district = 'Dakshina Kannada'
ORDER BY hierarchy;

-- Show summary
SELECT 
    'Installation Complete!' as status,
    'Panchayat Raj System integrated successfully' as message;
