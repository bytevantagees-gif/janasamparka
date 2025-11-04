-- Migration: Add work approval fields to complaints table
-- Phase 2: Before/After Photo Workflow Enhancement
-- Date: 2025-10-27

-- Add approval fields to complaints table
ALTER TABLE complaints
ADD COLUMN IF NOT EXISTS work_approved BOOLEAN DEFAULT NULL,
ADD COLUMN IF NOT EXISTS approval_comments TEXT,
ADD COLUMN IF NOT EXISTS approved_at TIMESTAMP,
ADD COLUMN IF NOT EXISTS approved_by UUID REFERENCES users(id),
ADD COLUMN IF NOT EXISTS rejection_reason TEXT,
ADD COLUMN IF NOT EXISTS rejected_at TIMESTAMP,
ADD COLUMN IF NOT EXISTS rejected_by UUID REFERENCES users(id);

-- Add photo_type and caption to media table
ALTER TABLE media
ADD COLUMN IF NOT EXISTS photo_type VARCHAR(20),
ADD COLUMN IF NOT EXISTS caption TEXT;

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_complaints_work_approved ON complaints(work_approved);
CREATE INDEX IF NOT EXISTS idx_media_photo_type ON media(photo_type);

-- Add comments for documentation
COMMENT ON COLUMN complaints.work_approved IS 'NULL=pending approval, TRUE=approved, FALSE=rejected';
COMMENT ON COLUMN complaints.approval_comments IS 'MLA comments when approving work';
COMMENT ON COLUMN complaints.rejection_reason IS 'Reason for rejecting completed work';
COMMENT ON COLUMN media.photo_type IS 'Type of photo: before, after, during, evidence';
COMMENT ON COLUMN media.caption IS 'Optional caption/description for the media';
