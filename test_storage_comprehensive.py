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

print("Comprehensive Storage Verification")
print("=" * 50)

# Check 1: List all buckets with detailed info
print("1. Checking all storage buckets:")
try:
    buckets = supabase.storage.list_buckets()
    if buckets:
        print(f"   ✓ Found {len(buckets)} bucket(s):")
        for i, bucket in enumerate(buckets):
            print(f"     Bucket {i+1}:")
            print(f"       Name: {bucket.name}")
            print(f"       ID: {bucket.id}")
            print(f"       Public: {getattr(bucket, 'public', 'Unknown')}")
            print(f"       Created: {getattr(bucket, 'created_at', 'Unknown')}")
            print()
    else:
        print("   ⚠ No buckets found")
except Exception as e:
    print(f"   ✗ Error listing buckets: {str(e)}")

# Check 2: Try common bucket names
print("2. Checking for common bucket names:")
common_names = ['videos', 'video', 'uploads', 'files', 'storage']
found_bucket = False

for name in common_names:
    try:
        bucket_info = supabase.storage.get_bucket(name)
        print(f"   ✓ Found bucket: {name}")
        found_bucket = True
        break
    except Exception:
        pass

if not found_bucket:
    print("   ⚠ No common bucket names found")

# Check 3: Try to create the videos bucket if it doesn't exist
print("\n3. Attempting to create 'videos' bucket:")
try:
    # Try to create the bucket
    response = supabase.storage.create_bucket('videos', {
        'public': False  # Private bucket for security
    })
    print("   ✓ Successfully created 'videos' bucket")
    print(f"   Bucket ID: {response.get('id', 'Unknown')}")
except Exception as e:
    error_msg = str(e).lower()
    if 'already exists' in error_msg or 'duplicate' in error_msg:
        print("   ⚠ Bucket 'videos' already exists")
    else:
        print(f"   ⚠ Could not create bucket: {str(e)}")

print("\n" + "=" * 50)
print("RECOMMENDATIONS:")
print("-" * 15)
print("1. Check your Supabase dashboard to verify bucket creation")
print("2. Make sure you're logged in with the correct account")
print("3. Verify bucket policies allow authenticated users to read/write")
print("4. If the bucket exists but isn't accessible, check the RLS policies")