# Supabase Database Setup

This document contains all the SQL queries needed to set up your Supabase database for the Executive Presence application.

## Table of Contents
1. [Extensions](#extensions)
2. [Tables](#tables)
   - [Users](#users-table)
   - [Videos](#videos-table)
   - [Jobs](#jobs-table)
   - [Reports](#reports-table)
   - [Profiles](#profiles-table)
   - [Subscriptions](#subscriptions-table)
   - [Shared Reports](#shared-reports-table)
3. [Row Level Security (RLS)](#row-level-security)
4. [Storage Configuration](#storage-configuration)
5. [Functions and Triggers](#functions-and-triggers)
6. [Permissions](#permissions)
7. [Indexes](#indexes)

## Extensions

```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

## Tables

### Users Table

```sql
CREATE TABLE IF NOT EXISTS public.users (
    id UUID REFERENCES auth.users ON DELETE CASCADE PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    name TEXT,
    picture TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Videos Table

```sql
CREATE TABLE IF NOT EXISTS public.videos (
    id TEXT PRIMARY KEY,
    user_id UUID REFERENCES public.users ON DELETE CASCADE NOT NULL,
    filename TEXT NOT NULL,
    file_path TEXT,
    content_type TEXT,
    size INTEGER,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    retention_policy TEXT DEFAULT '30_days',
    scheduled_deletion TIMESTAMP WITH TIME ZONE
);
```

### Jobs Table

```sql
CREATE TABLE IF NOT EXISTS public.jobs (
    id TEXT PRIMARY KEY,
    user_id UUID REFERENCES public.users ON DELETE CASCADE NOT NULL,
    video_id TEXT REFERENCES public.videos ON DELETE CASCADE,
    status TEXT DEFAULT 'pending',
    progress INTEGER DEFAULT 0,
    current_step TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Reports Table

```sql
CREATE TABLE IF NOT EXISTS public.reports (
    id TEXT PRIMARY KEY,
    user_id UUID REFERENCES public.users ON DELETE CASCADE NOT NULL,
    video_id TEXT REFERENCES public.videos ON DELETE CASCADE,
    job_id TEXT REFERENCES public.jobs ON DELETE CASCADE,
    transcript TEXT,
    overall_score NUMERIC(5,2),
    gravitas_score NUMERIC(5,2),
    communication_score NUMERIC(5,2),
    presence_score NUMERIC(5,2),
    storytelling_score NUMERIC(5,2),
    detailed_metrics JSONB,
    coaching_tips JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Profiles Table

```sql
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID REFERENCES auth.users ON DELETE CASCADE PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    company TEXT,
    role TEXT,
    industry TEXT,
    experience_level TEXT,
    communication_goals TEXT[],
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Subscriptions Table

```sql
CREATE TABLE IF NOT EXISTS public.subscriptions (
    id TEXT PRIMARY KEY,
    user_id UUID REFERENCES public.users ON DELETE CASCADE NOT NULL,
    plan_type TEXT NOT NULL,
    status TEXT DEFAULT 'active',
    start_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    end_date TIMESTAMP WITH TIME ZONE,
    auto_renew BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Shared Reports Table

```sql
CREATE TABLE IF NOT EXISTS public.shared_reports (
    id TEXT PRIMARY KEY,
    report_id TEXT REFERENCES public.reports ON DELETE CASCADE NOT NULL,
    owner_id UUID REFERENCES public.users ON DELETE CASCADE NOT NULL,
    shared_with_email TEXT NOT NULL,
    shared_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE
);
```

## Row Level Security

Enable RLS for all tables:

```sql
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.videos ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.shared_reports ENABLE ROW LEVEL SECURITY;
```

### Users Table Policies

```sql
CREATE POLICY "Users can view their own data" ON public.users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can insert their own data" ON public.users
    FOR INSERT WITH CHECK (auth.uid() = id);

CREATE POLICY "Users can update their own data" ON public.users
    FOR UPDATE USING (auth.uid() = id);
```

### Videos Table Policies

```sql
CREATE POLICY "Users can view their own videos" ON public.videos
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own videos" ON public.videos
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own videos" ON public.videos
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own videos" ON public.videos
    FOR DELETE USING (auth.uid() = user_id);
```

### Jobs Table Policies

```sql
CREATE POLICY "Users can view their own jobs" ON public.jobs
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own jobs" ON public.jobs
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own jobs" ON public.jobs
    FOR UPDATE USING (auth.uid() = user_id);
```

### Reports Table Policies

```sql
CREATE POLICY "Users can view their own reports" ON public.reports
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own reports" ON public.reports
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own reports" ON public.reports
    FOR UPDATE USING (auth.uid() = user_id);
```

### Profiles Table Policies

```sql
CREATE POLICY "Profiles are viewable by owner" ON public.profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can insert their own profile" ON public.profiles
    FOR INSERT WITH CHECK (auth.uid() = id);

CREATE POLICY "Users can update their own profile" ON public.profiles
    FOR UPDATE USING (auth.uid() = id);
```

### Subscriptions Table Policies

```sql
CREATE POLICY "Users can view their own subscriptions" ON public.subscriptions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own subscriptions" ON public.subscriptions
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own subscriptions" ON public.subscriptions
    FOR UPDATE USING (auth.uid() = user_id);
```

### Shared Reports Table Policies

```sql
CREATE POLICY "Users can view reports shared with them or owned by them" ON public.shared_reports
    FOR SELECT USING (auth.uid() = owner_id OR shared_with_email = (SELECT email FROM public.users WHERE id = auth.uid()));

CREATE POLICY "Users can share their own reports" ON public.shared_reports
    FOR INSERT WITH CHECK (auth.uid() = owner_id);

CREATE POLICY "Owners can delete shared reports" ON public.shared_reports
    FOR DELETE USING (auth.uid() = owner_id);
```

## Storage Configuration

Create a storage bucket named `videos` through the Supabase dashboard.

Storage policies for the `videos` bucket:

```
-- Select Policy
FOR SELECT USING (bucket_id = 'videos' AND (auth.role() = 'authenticated'));

-- Insert Policy  
FOR INSERT WITH CHECK (bucket_id = 'videos' AND auth.role() = 'authenticated' AND (SELECT auth.uid()) = owner_id);

-- Update Policy
FOR UPDATE USING (bucket_id = 'videos' AND auth.role() = 'authenticated' AND (SELECT auth.uid()) = owner_id);

-- Delete Policy
FOR DELETE USING (bucket_id = 'videos' AND auth.role() = 'authenticated' AND (SELECT auth.uid()) = owner_id);
```

## Functions and Triggers

### Handle New User Function

```sql
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.users (id, email, name, created_at)
  VALUES (NEW.id, NEW.email, NEW.raw_user_meta_data->>'name', NEW.created_at);
  
  INSERT INTO public.profiles (id, first_name, last_name)
  VALUES (NEW.id, 
          SPLIT_PART(NEW.raw_user_meta_data->>'name', ' ', 1),
          SPLIT_PART(NEW.raw_user_meta_data->>'name', ' ', 2));
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

### Trigger for New User Creation

```sql
CREATE OR REPLACE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();
```

## Permissions

```sql
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT ALL ON TABLE public.users TO authenticated;
GRANT ALL ON TABLE public.videos TO authenticated;
GRANT ALL ON TABLE public.jobs TO authenticated;
GRANT ALL ON TABLE public.reports TO authenticated;
GRANT ALL ON TABLE public.profiles TO authenticated;
GRANT ALL ON TABLE public.subscriptions TO authenticated;
GRANT ALL ON TABLE public.shared_reports TO authenticated;

-- Grant SELECT on auth.users to authenticated users (needed for some queries)
GRANT SELECT ON TABLE auth.users TO authenticated;
```

## Indexes

```sql
CREATE INDEX IF NOT EXISTS idx_videos_user_id ON public.videos(user_id);
CREATE INDEX IF NOT EXISTS idx_jobs_user_id ON public.jobs(user_id);
CREATE INDEX IF NOT EXISTS idx_reports_user_id ON public.reports(user_id);
CREATE INDEX IF NOT EXISTS idx_reports_video_id ON public.reports(video_id);
CREATE INDEX IF NOT EXISTS idx_shared_reports_owner_id ON public.shared_reports(owner_id);
CREATE INDEX IF NOT EXISTS idx_shared_reports_shared_with_email ON public.shared_reports(shared_with_email);
```