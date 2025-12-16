#!/usr/bin/env python3
"""
Simple test script to verify that the videos bucket is accessible
after setting up policies.
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

def test_bucket_access():
    """Test if the videos bucket is accessible"""
    print("Testing Videos Bucket Access")
    print("=" * 30)
    
    # Get Supabase credentials
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
        return False
    
    try:
        # Create Supabase client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Supabase client created successfully")
        
        # Test 1: List buckets
        print("\n1. Listing storage buckets...")
        buckets = supabase.storage.list_buckets()
        print(f"   Found {len(buckets)} bucket(s)")
        
        # Check if videos bucket exists
        videos_bucket = next((b for b in buckets if b.name == 'videos'), None)
        if videos_bucket:
            print("   ✅ Videos bucket found")
        else:
            print("   ❌ Videos bucket not found")
            return False
            
        # Test 2: Access videos bucket directly
        print("\n2. Accessing videos bucket directly...")
        bucket_info = supabase.storage.get_bucket('videos')
        print(f"   ✅ Videos bucket accessible: {bucket_info.name}")
        
        # Test 3: Try to upload a small test file
        print("\n3. Testing file upload...")
        test_content = b"This is a test file to verify bucket access"
        
        response = supabase.storage.from_('videos').upload(
            file=test_content,
            path='test-access.txt',
            file_options={"content-type": "text/plain"}
        )
        print("   ✅ File upload successful")
        
        # Test 4: Clean up test file
        print("\n4. Cleaning up test file...")
        supabase.storage.from_('videos').remove(['test-access.txt'])
        print("   ✅ Test file cleaned up")
        
        print("\n" + "=" * 50)
        print("🎉 ALL TESTS PASSED!")
        print("The videos bucket is properly configured and accessible!")
        print("Your application should now work correctly with video storage.")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\n🔧 Troubleshooting steps:")
        print("1. Verify you've added all the required policies to the videos bucket")
        print("2. Check that your service role key has storage permissions")
        print("3. Make sure the bucket name is exactly 'videos'")
        print("4. Restart your application after making changes")
        return False

if __name__ == "__main__":
    test_bucket_access()