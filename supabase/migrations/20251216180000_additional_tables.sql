-- Create Coaching Requests table
CREATE TABLE IF NOT EXISTS public.coaching_requests (
    id TEXT PRIMARY KEY,
    user_id UUID REFERENCES public.users ON DELETE CASCADE NOT NULL,
    name TEXT,
    email TEXT,
    goal TEXT,
    preferred_times TEXT,
    notes TEXT,
    report_id TEXT REFERENCES public.reports ON DELETE SET NULL,
    status TEXT DEFAULT 'new',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create Devices table for device fingerprint tracking
CREATE TABLE IF NOT EXISTS public.devices (
    id TEXT PRIMARY KEY,
    user_id UUID REFERENCES public.users ON DELETE CASCADE NOT NULL,
    fingerprint TEXT UNIQUE NOT NULL,
    last_seen TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create User Sessions table for custom session management
CREATE TABLE IF NOT EXISTS public.user_sessions (
    id TEXT PRIMARY KEY,
    user_id UUID REFERENCES public.users ON DELETE CASCADE NOT NULL,
    session_token TEXT UNIQUE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS for new tables
ALTER TABLE public.coaching_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.devices ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_sessions ENABLE ROW LEVEL SECURITY;

-- Policies for Coaching Requests table
CREATE POLICY "Users can view their own coaching requests" ON public.coaching_requests
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create coaching requests" ON public.coaching_requests
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own coaching requests" ON public.coaching_requests
    FOR UPDATE USING (auth.uid() = user_id);

-- Policies for Devices table
CREATE POLICY "Users can view their own devices" ON public.devices
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can register their own devices" ON public.devices
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own devices" ON public.devices
    FOR UPDATE USING (auth.uid() = user_id);

-- Policies for User Sessions table
CREATE POLICY "Users can view their own sessions" ON public.user_sessions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create their own sessions" ON public.user_sessions
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their own sessions" ON public.user_sessions
    FOR DELETE USING (auth.uid() = user_id);

-- Grant Permissions for new tables
GRANT ALL ON TABLE public.coaching_requests TO authenticated;
GRANT ALL ON TABLE public.devices TO authenticated;
GRANT ALL ON TABLE public.user_sessions TO authenticated;

-- Indexes for Performance
CREATE INDEX IF NOT EXISTS idx_coaching_requests_user_id ON public.coaching_requests(user_id);
CREATE INDEX IF NOT EXISTS idx_devices_user_id ON public.devices(user_id);
CREATE INDEX IF NOT EXISTS idx_devices_fingerprint ON public.devices(fingerprint);
CREATE INDEX IF NOT EXISTS idx_user_sessions_token ON public.user_sessions(session_token);
CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON public.user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_expires_at ON public.user_sessions(expires_at);
