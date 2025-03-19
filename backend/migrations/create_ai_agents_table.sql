-- Create the ai_agents table
CREATE TABLE public.ai_agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    model_id VARCHAR(100) NOT NULL,
    tool_categories JSONB DEFAULT '[]'::jsonb,
    custom_instructions TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    is_active BOOLEAN NOT NULL DEFAULT true,
    chat_history JSONB DEFAULT '[]'::jsonb,
    usage_count INTEGER NOT NULL DEFAULT 0,
    last_used_at TIMESTAMPTZ,
    configuration JSONB DEFAULT '{}'::jsonb
);

-- Create an index on user_id for faster queries
CREATE INDEX idx_ai_agents_user_id ON public.ai_agents(user_id);

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create a trigger to automatically update the updated_at column
CREATE TRIGGER update_ai_agents_updated_at
BEFORE UPDATE ON public.ai_agents
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security
ALTER TABLE public.ai_agents ENABLE ROW LEVEL SECURITY;

-- Create policies for Row Level Security
-- 1. Users can view only their own agents
CREATE POLICY "Users can view their own agents"
    ON public.ai_agents
    FOR SELECT
    USING (auth.uid() = user_id);

-- 2. Users can insert their own agents
CREATE POLICY "Users can insert their own agents"
    ON public.ai_agents
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- 3. Users can update their own agents
CREATE POLICY "Users can update their own agents"
    ON public.ai_agents
    FOR UPDATE
    USING (auth.uid() = user_id);

-- 4. Users can delete their own agents
CREATE POLICY "Users can delete their own agents"
    ON public.ai_agents
    FOR DELETE
    USING (auth.uid() = user_id);

-- Grant permissions to authenticated users
GRANT SELECT, INSERT, UPDATE, DELETE ON public.ai_agents TO authenticated;

-- Create a function to increment usage_count and update last_used_at
CREATE OR REPLACE FUNCTION increment_agent_usage(agent_id UUID)
RETURNS VOID AS $$
BEGIN
    UPDATE public.ai_agents
    SET 
        usage_count = usage_count + 1,
        last_used_at = now()
    WHERE id = agent_id;
END;
$$ LANGUAGE plpgsql;

-- Grant execute permission on the function
GRANT EXECUTE ON FUNCTION increment_agent_usage TO authenticated;

-- Comments for documentation
COMMENT ON TABLE public.ai_agents IS 'Stores AI agents created by users';
COMMENT ON COLUMN public.ai_agents.id IS 'Unique identifier for the agent';
COMMENT ON COLUMN public.ai_agents.user_id IS 'Reference to the user who created the agent';
COMMENT ON COLUMN public.ai_agents.name IS 'Name of the agent';
COMMENT ON COLUMN public.ai_agents.description IS 'Description of the agent and its purpose';
COMMENT ON COLUMN public.ai_agents.model_id IS 'ID of the AI model used by the agent';
COMMENT ON COLUMN public.ai_agents.tool_categories IS 'JSON array of tool categories the agent can use';
COMMENT ON COLUMN public.ai_agents.custom_instructions IS 'Custom instructions for the agent';
COMMENT ON COLUMN public.ai_agents.created_at IS 'Timestamp when the agent was created';
COMMENT ON COLUMN public.ai_agents.updated_at IS 'Timestamp when the agent was last updated';
COMMENT ON COLUMN public.ai_agents.is_active IS 'Whether the agent is active or disabled';
COMMENT ON COLUMN public.ai_agents.usage_count IS 'Number of times the agent has been used';
COMMENT ON COLUMN public.ai_agents.last_used_at IS 'Timestamp when the agent was last used';
COMMENT ON COLUMN public.ai_agents.configuration IS 'JSON object with additional configuration options'; 