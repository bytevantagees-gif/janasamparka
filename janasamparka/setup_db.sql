-- Setup script for Janasamparka database
-- Run this with: psql < setup_db.sql

-- Drop database if exists (careful - deletes data!)
DROP DATABASE IF EXISTS janasamparka_db;

-- Create fresh database
CREATE DATABASE janasamparka_db;

-- Connect to the new database
\c janasamparka_db

-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;

-- Verify
SELECT PostGIS_Version();
