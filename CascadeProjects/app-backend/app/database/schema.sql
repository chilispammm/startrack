-- Create submissions table
CREATE TABLE IF NOT EXISTS submissions (
    id UUID PRIMARY KEY,
    full_name TEXT NOT NULL,
    user_email TEXT NOT NULL,
    company_email TEXT NOT NULL,
    job_title TEXT NOT NULL,
    email_subject TEXT NOT NULL,
    email_body TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    cv_url TEXT,
    status TEXT DEFAULT 'pending',
    response_received BOOLEAN DEFAULT FALSE,
    response_details JSONB
);

-- Create indexes
CREATE INDEX idx_submissions_timestamp ON submissions(timestamp);
CREATE INDEX idx_submissions_user_email ON submissions(user_email);
CREATE INDEX idx_submissions_company_email ON submissions(company_email);
CREATE INDEX idx_submissions_status ON submissions(status);

-- Enable row level security
ALTER TABLE submissions ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Users can view their own submissions"
    ON submissions FOR SELECT
    USING (user_email = auth.email());

CREATE POLICY "Admins can view all submissions"
    ON submissions FOR SELECT
    USING (auth.role() = 'service_role');

-- Create storage bucket for CVs
-- This will be done via Supabase UI or API, not SQL
