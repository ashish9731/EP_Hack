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

print("Checking Supabase tables...")
print("=" * 50)

try:
    # Check if tables exist by querying the information schema
    response = supabase.table('users').select('*').limit(1).execute()
    print("✓ Connected to Supabase successfully")
    print("✓ Users table exists")
    
    # Check other tables
    tables_to_check = [
        'videos', 'jobs', 'reports', 'profiles', 
        'subscriptions', 'shared_reports', 'coaching_requests', 'devices'
    ]
    
    existing_tables = []
    missing_tables = []
    
    for table in tables_to_check:
        try:
            response = supabase.table(table).select('*').limit(1).execute()
            print(f"✓ {table.capitalize()} table exists")
            existing_tables.append(table)
        except Exception as e:
            print(f"✗ {table.capitalize()} table is missing: {str(e)[:50]}...")
            missing_tables.append(table)
            
    print("\n" + "=" * 50)
    print(f"Existing tables ({len(existing_tables)}): {', '.join(existing_tables)}")
    print(f"Missing tables ({len(missing_tables)}): {', '.join(missing_tables)}")
    
    if missing_tables:
        print(f"\nNeed to create {len(missing_tables)} tables:")
        for table in missing_tables:
            print(f"  - {table}")
    else:
        print("\n✅ All required tables exist!")
    
except Exception as e:
    print(f"Error connecting to Supabase: {str(e)}")
    print("Please check your SUPABASE_URL and SUPABASE_KEY in the .env file")