import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Get Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
    sys.exit(1)

# Create Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("Creating missing tables...")
print("=" * 50)

try:
    # Create coaching_requests table
    print("Creating coaching_requests table...")
    
    # Note: We can't directly create tables through the Supabase client
    # We need to use the REST API or SQL commands
    
    # Let's try to insert a dummy record to trigger table creation
    # This won't work for creating tables, but let's try a different approach
    
    print("Cannot create tables directly through the client.")
    print("Please use the Supabase SQL editor in the dashboard to run:")
    print()
    print("-- Create Coaching Requests table")
    print("CREATE TABLE IF NOT EXISTS public.coaching_requests (")
    print("    id TEXT PRIMARY KEY,")
    print("    user_id UUID REFERENCES public.users ON DELETE CASCADE NOT NULL,")
    print("    name TEXT,")
    print("    email TEXT,")
    print("    goal TEXT,")
    print("    preferred_times TEXT,")
    print("    notes TEXT,")
    print("    report_id TEXT REFERENCES public.reports ON DELETE SET NULL,")
    print("    status TEXT DEFAULT 'new',")
    print("    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),")
    print("    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()")
    print(");")
    print()
    print("-- Create Devices table")
    print("CREATE TABLE IF NOT EXISTS public.devices (")
    print("    id TEXT PRIMARY KEY,")
    print("    user_id UUID REFERENCES public.users ON DELETE CASCADE NOT NULL,")
    print("    fingerprint TEXT UNIQUE NOT NULL,")
    print("    last_seen TIMESTAMP WITH TIME ZONE DEFAULT NOW()")
    print(");")
    
except Exception as e:
    print(f"Error: {str(e)}")