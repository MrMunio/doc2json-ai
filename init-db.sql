-- Database initialization script
-- This runs automatically when the PostgreSQL container starts for the first time

-- Create schema if it doesn't exist
CREATE SCHEMA IF NOT EXISTS public;

-- Create the extraction_tracker table
CREATE TABLE IF NOT EXISTS public.extraction_tracker (
    request_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id VARCHAR(255) NOT NULL,
    metadata JSONB NOT NULL,
    status VARCHAR(50) NOT NULL,
    extracted_data JSONB,
    message TEXT,
    errors JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_application_id ON public.extraction_tracker (application_id);
CREATE INDEX IF NOT EXISTS idx_metadata_checksum ON public.extraction_tracker USING gin (metadata);

-- Log completion
DO $$
BEGIN
    RAISE NOTICE 'Database initialization completed successfully';
END $$;
