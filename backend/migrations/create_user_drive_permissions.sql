CREATE TABLE user_drive_permissions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    file_id TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, file_id)
);

-- Add RLS (Row Level Security) policies
ALTER TABLE user_drive_permissions ENABLE ROW LEVEL SECURITY;

-- Policy to allow users to read only their own permissions
CREATE POLICY "Users can view their own drive permissions"
ON user_drive_permissions
FOR SELECT
TO authenticated
USING (auth.uid() = user_id);

-- Policy to allow service role to manage all permissions
CREATE POLICY "Service role can manage all permissions"
ON user_drive_permissions
TO service_role
USING (true)
WITH CHECK (true);

-- Create an index for faster lookups
CREATE INDEX idx_user_drive_permissions_user_id ON user_drive_permissions(user_id);