-- PostGIS Setup for Janasamparka
-- Phase 2.3: Spatial Queries and Ward Detection
-- Date: 2025-10-27

-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- Add geometry column to wards table
ALTER TABLE wards
ADD COLUMN IF NOT EXISTS boundary GEOMETRY(POLYGON, 4326);

-- Create spatial index on ward boundaries
CREATE INDEX IF NOT EXISTS idx_wards_boundary_gist ON wards USING GIST (boundary);

-- Add center point column (optional - for ward center markers)
ALTER TABLE wards
ADD COLUMN IF NOT EXISTS center_point GEOMETRY(POINT, 4326);

-- Create spatial index on center points
CREATE INDEX IF NOT EXISTS idx_wards_center_gist ON wards USING GIST (center_point);

-- Add geometry column to complaints for spatial queries
ALTER TABLE complaints
ADD COLUMN IF NOT EXISTS location_point GEOMETRY(POINT, 4326);

-- Create spatial index on complaint locations
CREATE INDEX IF NOT EXISTS idx_complaints_location_gist ON complaints USING GIST (location_point);

-- Create trigger to auto-update location_point from lat/lng
CREATE OR REPLACE FUNCTION update_complaint_location_point()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.lat IS NOT NULL AND NEW.lng IS NOT NULL THEN
        NEW.location_point := ST_SetSRID(ST_MakePoint(NEW.lng, NEW.lat), 4326);
    ELSE
        NEW.location_point := NULL;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Attach trigger to complaints table
DROP TRIGGER IF EXISTS complaint_location_point_trigger ON complaints;
CREATE TRIGGER complaint_location_point_trigger
BEFORE INSERT OR UPDATE OF lat, lng ON complaints
FOR EACH ROW
EXECUTE FUNCTION update_complaint_location_point();

-- Function to find ward from coordinates using PostGIS
CREATE OR REPLACE FUNCTION find_ward_from_coordinates(
    p_lat NUMERIC,
    p_lng NUMERIC
)
RETURNS TABLE (
    ward_id UUID,
    ward_name VARCHAR,
    ward_number VARCHAR,
    constituency_id UUID,
    distance_km NUMERIC
) AS $$
BEGIN
    -- Create point from coordinates
    DECLARE
        point_geom GEOMETRY;
    BEGIN
        point_geom := ST_SetSRID(ST_MakePoint(p_lng, p_lat), 4326);
        
        -- First try: Find ward containing the point
        RETURN QUERY
        SELECT 
            w.id,
            w.name,
            w.ward_number,
            w.constituency_id,
            0::NUMERIC as distance_km
        FROM wards w
        WHERE ST_Contains(w.boundary, point_geom)
        LIMIT 1;
        
        -- If no exact match, find nearest ward
        IF NOT FOUND THEN
            RETURN QUERY
            SELECT 
                w.id,
                w.name,
                w.ward_number,
                w.constituency_id,
                ROUND((ST_Distance(
                    w.boundary::geography,
                    point_geom::geography
                ) / 1000)::NUMERIC, 2) as distance_km
            FROM wards w
            WHERE w.boundary IS NOT NULL
            ORDER BY w.boundary <-> point_geom
            LIMIT 1;
        END IF;
    END;
END;
$$ LANGUAGE plpgsql;

-- Function to get complaints within radius (km)
CREATE OR REPLACE FUNCTION get_complaints_within_radius(
    p_lat NUMERIC,
    p_lng NUMERIC,
    radius_km NUMERIC DEFAULT 5
)
RETURNS TABLE (
    complaint_id UUID,
    title VARCHAR,
    distance_km NUMERIC
) AS $$
DECLARE
    point_geom GEOMETRY;
BEGIN
    point_geom := ST_SetSRID(ST_MakePoint(p_lng, p_lat), 4326);
    
    RETURN QUERY
    SELECT 
        c.id,
        c.title,
        ROUND((ST_Distance(
            c.location_point::geography,
            point_geom::geography
        ) / 1000)::NUMERIC, 2) as distance_km
    FROM complaints c
    WHERE c.location_point IS NOT NULL
      AND ST_DWithin(
          c.location_point::geography,
          point_geom::geography,
          radius_km * 1000  -- Convert km to meters
      )
    ORDER BY distance_km;
END;
$$ LANGUAGE plpgsql;

-- Function to cluster complaints using ST_ClusterDBSCAN
CREATE OR REPLACE FUNCTION cluster_complaints(
    eps_meters NUMERIC DEFAULT 1000,
    min_points INTEGER DEFAULT 3
)
RETURNS TABLE (
    cluster_id INTEGER,
    complaint_ids UUID[],
    center_lat NUMERIC,
    center_lng NUMERIC,
    complaint_count BIGINT
) AS $$
BEGIN
    RETURN QUERY
    WITH clustered AS (
        SELECT 
            c.id,
            c.location_point,
            ST_ClusterDBSCAN(
                c.location_point::geography,
                eps := eps_meters,
                minpoints := min_points
            ) OVER () as cluster_num
        FROM complaints c
        WHERE c.location_point IS NOT NULL
    ),
    cluster_summary AS (
        SELECT 
            cluster_num,
            array_agg(id) as ids,
            ST_Centroid(ST_Collect(location_point)) as center,
            COUNT(*) as count
        FROM clustered
        WHERE cluster_num IS NOT NULL
        GROUP BY cluster_num
    )
    SELECT 
        cluster_num::INTEGER,
        ids,
        ST_Y(center)::NUMERIC as lat,
        ST_X(center)::NUMERIC as lng,
        count
    FROM cluster_summary
    ORDER BY count DESC;
END;
$$ LANGUAGE plpgsql;

-- Add comments for documentation
COMMENT ON COLUMN wards.boundary IS 'Ward boundary as PostGIS polygon (SRID 4326)';
COMMENT ON COLUMN wards.center_point IS 'Ward center point for map markers';
COMMENT ON COLUMN complaints.location_point IS 'Complaint location as PostGIS point (auto-generated from lat/lng)';
COMMENT ON FUNCTION find_ward_from_coordinates IS 'Find ward containing given coordinates, or nearest ward if no exact match';
COMMENT ON FUNCTION get_complaints_within_radius IS 'Get all complaints within specified radius (km) of a point';
COMMENT ON FUNCTION cluster_complaints IS 'Cluster complaints using DBSCAN algorithm';

-- Sample query examples (commented out)
/*
-- Example 1: Find ward for coordinates
SELECT * FROM find_ward_from_coordinates(12.7626, 75.2150);

-- Example 2: Get complaints within 5km
SELECT * FROM get_complaints_within_radius(12.7626, 75.2150, 5);

-- Example 3: Cluster complaints
SELECT * FROM cluster_complaints(1000, 3);

-- Example 4: Count complaints per ward
SELECT 
    w.name,
    w.ward_number,
    COUNT(c.id) as complaint_count
FROM wards w
LEFT JOIN complaints c ON ST_Contains(w.boundary, c.location_point)
GROUP BY w.id, w.name, w.ward_number
ORDER BY complaint_count DESC;
*/
