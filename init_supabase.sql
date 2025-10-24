-- ============================================
-- Supabase Table Schema for ToDo App
-- ============================================
-- 
-- INSTRUCTIONS:
-- 1. Go to your Supabase project dashboard
-- 2. Navigate to SQL Editor
-- 3. Copy and paste this entire script
-- 4. Click "Run" to create the table
-- 
-- ============================================

CREATE TABLE IF NOT EXISTS tasks (
    id BIGSERIAL PRIMARY KEY,
    description TEXT NOT NULL,
    completed BOOLEAN DEFAULT FALSE,
    due_date DATE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add Row Level Security (RLS) policies if needed
-- Uncomment the following lines to enable RLS:

-- ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;

-- Example: Allow all operations for authenticated users
-- CREATE POLICY "Enable all operations for authenticated users" 
--   ON tasks 
--   FOR ALL 
--   USING (auth.role() = 'authenticated');

-- Example: Allow all operations for everyone (public access)
-- CREATE POLICY "Enable all operations for everyone" 
--   ON tasks 
--   FOR ALL 
--   USING (true);

