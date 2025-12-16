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

print("Checking Supabase storage...")
print("=" * 50)

try:
    # List storage buckets
    response = supabase.storage.list_buckets()
    print("✓ Connected to Supabase storage successfully")
    
    if response:
        print(f"✓ Found {len(response)} storage bucket(s):")
        for bucket in response:
            print(f"  - {bucket.name} (id: {bucket.id})")
    else:
        print("⚠ No storage buckets found")
        print("  Please create a 'videos' bucket in the Supabase dashboard")
        
except Exception as e:
    print(f"⚠ Could not access storage: {str(e)}")
    print("  This might be because the 'videos' bucket hasn't been created yet")

print("\nNext steps:")
print("-" * 20)
print("1. Go to your Supabase dashboard")
print("2. Navigate to Storage → Buckets")
print("3. Create a new bucket named 'videos'")
print("4. Set appropriate policies for the bucket")