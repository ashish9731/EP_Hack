-- Enable necessary extensions
create extension if not exists "uuid-ossp";

-- Create users table
create table if not exists users (
  id uuid references auth.users on delete cascade not null primary key,
  email text unique not null,
  name text,
  picture text,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Create user_sessions table
create table if not exists user_sessions (
  id uuid default uuid_generate_v4() primary key,
  user_id uuid references users(id) on delete cascade not null,
  session_token text unique not null,
  expires_at timestamp with time zone not null,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Create profiles table
create table if not exists profiles (
  id uuid references auth.users on delete cascade not null primary key,
  first_name text,
  last_name text,
  company text,
  role text,
  industry text,
  seniority_level text,
  communication_goals text[],
  updated_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Create videos table
create table if not exists videos (
  id uuid default uuid_generate_v4() primary key,
  user_id uuid references users(id) on delete cascade not null,
  filename text not null,
  file_size bigint,
  format text,
  uploaded_at timestamp with time zone default timezone('utc'::text, now()) not null,
  retention_policy text,
  scheduled_deletion timestamp with time zone
);

-- Create video_jobs table
create table if not exists video_jobs (
  id uuid default uuid_generate_v4() primary key,
  user_id uuid references users(id) on delete cascade not null,
  video_id uuid references videos(id) on delete cascade not null,
  status text not null,
  progress integer,
  current_step text,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  updated_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Create ep_reports table
create table if not exists ep_reports (
  id uuid default uuid_generate_v4() primary key,
  user_id uuid references users(id) on delete cascade not null,
  video_id uuid references videos(id) on delete cascade,
  job_id uuid references video_jobs(id) on delete cascade,
  transcript text,
  overall_score numeric(5,2),
  gravitas_score numeric(5,2),
  communication_score numeric(5,2),
  presence_score numeric(5,2),
  storytelling_score numeric(5,2),
  detailed_metrics jsonb,
  coaching_tips text[],
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Create subscriptions table
create table if not exists subscriptions (
  id uuid default uuid_generate_v4() primary key,
  user_id uuid references users(id) on delete cascade not null,
  email text not null,
  tier text not null,
  status text not null,
  started_at timestamp with time zone default timezone('utc'::text, now()) not null,
  expires_at timestamp with time zone,
  videos_used_this_month integer default 0,
  device_fingerprints text[],
  is_whitelisted boolean default false
);

-- Create coaching_requests table
create table if not exists coaching_requests (
  id uuid default uuid_generate_v4() primary key,
  user_id uuid references users(id) on delete cascade not null,
  name text,
  email text,
  goal text,
  preferred_times text[],
  notes text,
  report_id uuid references ep_reports(id) on delete set null,
  status text not null,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  updated_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Create report_shares table
create table if not exists report_shares (
  id uuid default uuid_generate_v4() primary key,
  report_id uuid references ep_reports(id) on delete cascade not null,
  owner_user_id uuid references users(id) on delete cascade not null,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  expires_at timestamp with time zone,
  revoked boolean default false
);

-- Set up Row Level Security (RLS)
alter table users enable row level security;
alter table user_sessions enable row level security;
alter table profiles enable row level security;
alter table videos enable row level security;
alter table video_jobs enable row level security;
alter table ep_reports enable row level security;
alter table subscriptions enable row level security;
alter table coaching_requests enable row level security;
alter table report_shares enable row level security;

-- Create policies for users table
create policy "Users can view their own data" on users
  for select using (auth.uid() = id);

create policy "Users can insert their own data" on users
  for insert with check (auth.uid() = id);

create policy "Users can update their own data" on users
  for update using (auth.uid() = id);

-- Create policies for profiles table
create policy "Profiles are viewable by owner" on profiles
  for select using (auth.uid() = id);

create policy "Profiles are insertable by owner" on profiles
  for insert with check (auth.uid() = id);

create policy "Profiles are updateable by owner" on profiles
  for update using (auth.uid() = id);

-- Create policies for videos table
create policy "Videos are viewable by owner" on videos
  for select using (auth.uid() = user_id);

create policy "Videos are insertable by owner" on videos
  for insert with check (auth.uid() = user_id);

create policy "Videos are deletable by owner" on videos
  for delete using (auth.uid() = user_id);

-- Create policies for video_jobs table
create policy "Jobs are viewable by owner" on video_jobs
  for select using (auth.uid() = user_id);

create policy "Jobs are insertable by owner" on video_jobs
  for insert with check (auth.uid() = user_id);

-- Create policies for ep_reports table
create policy "Reports are viewable by owner" on ep_reports
  for select using (auth.uid() = user_id);

create policy "Reports are insertable by owner" on ep_reports
  for insert with check (auth.uid() = user_id);

-- Create policies for subscriptions table
create policy "Subscriptions are viewable by owner" on subscriptions
  for select using (auth.uid() = user_id);

create policy "Subscriptions are insertable by owner" on subscriptions
  for insert with check (auth.uid() = user_id);

create policy "Subscriptions are updateable by owner" on subscriptions
  for update using (auth.uid() = user_id);

-- Create policies for coaching_requests table
create policy "Coaching requests are viewable by owner" on coaching_requests
  for select using (auth.uid() = user_id);

create policy "Coaching requests are insertable by everyone" on coaching_requests
  for insert with check (true);

-- Create policies for report_shares table
create policy "Shares are viewable by owner" on report_shares
  for select using (auth.uid() = owner_user_id);

create policy "Shares are insertable by owner" on report_shares
  for insert with check (auth.uid() = owner_user_id);

-- Create function to handle new user creation
create or replace function public.handle_new_user()
returns trigger as $$
begin
  insert into public.users (id, email, name, created_at)
  values (new.id, new.email, new.raw_user_meta_data->>'name', new.created_at);
  
  insert into public.profiles (id)
  values (new.id);
  
  return new;
end;
$$ language plpgsql security definer;

-- Create trigger for new user creation
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure public.handle_new_user();

-- Create indexes for better performance
create index if not exists idx_videos_user_id on videos(user_id);
create index if not exists idx_video_jobs_user_id on video_jobs(user_id);
create index if not exists idx_video_jobs_video_id on video_jobs(video_id);
create index if not exists idx_ep_reports_user_id on ep_reports(user_id);
create index if not exists idx_ep_reports_video_id on ep_reports(video_id);
create index if not exists idx_user_sessions_token on user_sessions(session_token);
create index if not exists idx_user_sessions_user_id on user_sessions(user_id);
create index if not exists idx_subscriptions_user_id on subscriptions(user_id);
create index if not exists idx_coaching_requests_user_id on coaching_requests(user_id);
create index if not exists idx_report_shares_report_id on report_shares(report_id);