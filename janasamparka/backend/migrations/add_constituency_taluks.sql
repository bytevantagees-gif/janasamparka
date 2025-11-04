-- Migration: Add Multi-Taluk Support to Constituencies
-- Description: Allow one constituency to span multiple taluks (e.g., Puttur + Kadaba)
-- Date: 2024-10-30

-- Add taluks array column to constituencies table
ALTER TABLE constituencies
ADD COLUMN IF NOT EXISTS taluks TEXT[] DEFAULT '{}';

-- Add comment for documentation
COMMENT ON COLUMN constituencies.taluks IS 'Array of taluk names covered by this constituency (e.g., [''Puttur'', ''Kadaba''])';

-- Update existing constituencies with their taluks
-- Note: Adjust these based on actual constituency-taluk mappings

-- Puttur Constituency (covers Puttur and Kadaba taluks)
UPDATE constituencies
SET taluks = ARRAY['Puttur', 'Kadaba']
WHERE code = 'PUT001';

-- Mangalore Constituency (covers Mangalore taluk)
UPDATE constituencies
SET taluks = ARRAY['Mangalore']
WHERE code = 'MNG001';

-- Bantwal Constituency (covers Bantwal taluk)
UPDATE constituencies
SET taluks = ARRAY['Bantwal']
WHERE code = 'BAN001';

-- Create index for taluk queries (GIN index for array contains operations)
CREATE INDEX IF NOT EXISTS idx_constituencies_taluks 
ON constituencies USING GIN (taluks);

-- Example queries after migration:

-- Find all constituencies covering a specific taluk
-- SELECT * FROM constituencies WHERE 'Puttur' = ANY(taluks);

-- Find constituencies with multiple taluks
-- SELECT name, taluks FROM constituencies WHERE array_length(taluks, 1) > 1;

-- Get all taluks in system
-- SELECT DISTINCT unnest(taluks) as taluk FROM constituencies ORDER BY taluk;
