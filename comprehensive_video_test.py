#!/usr/bin/env python3

import requests
import time
import json
import subprocess
import os

def create_test_video():
    """Create a minimal test video file using ffmpeg"""
    output_file = "/tmp/test_video.mp4"
    
    command = [
        '/usr/bin/ffmpeg',
        '-f', 'lavfi',
        '-i', 'testsrc=duration=5:size=320x240:rate=1',
        '-f', 'lavfi', 
        '-i', 'sine=frequency=1000:duration=5',
        '-c:v', 'libx264',
        '-c:a', 'aac',
        '-shortest',
        '-y',
        output_file
    ]
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return output_file
        else:
            print(f"❌ Failed to create test video: {result.stderr}")
            return None
    except Exception as e:
        print(f"❌ Error creating test video: {e}")
        return None

def test_comprehensive_video_pipeline():
    base_url = "https://exec-presence.preview.emergentagent.com"
    session_token = "session_715dbc2d083042dba4122d189f6b55e4"
    
    print("🎬 COMPREHENSIVE VIDEO PROCESSING PIPELINE TEST")
    print("=" * 60)
    
    # Step 1: Create a real test video
    print("📹 Creating test video...")
    video_file_path = create_test_video()
    if not video_file_path:
        print("❌ Cannot create test video - stopping test")
        return False
    
    print(f"✅ Test video created: {os.path.getsize(video_file_path)} bytes")
    
    # Step 2: Login
    login_data = {
        "email": "uitest_golden@test.com",
        "password": "TestPass123!"
    }
    
    response = requests.post(f"{base_url}/api/auth/login", json=login_data)
    if response.status_code == 200:
        session_token = response.json()['session_token']
        print("✅ Authentication successful")
    else:
        print(f"❌ Login failed: {response.status_code}")
        return False
    
    headers = {'Authorization': f'Bearer {session_token}'}
    
    # Step 3: Upload real video
    print("\n📤 Uploading video...")
    with open(video_file_path, 'rb') as video_file:
        files = {
            'file': ('test_video.mp4', video_file, 'video/mp4')
        }
        
        response = requests.post(f"{base_url}/api/videos/upload", files=files, headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Video upload failed: {response.status_code} - {response.text}")
        return False
    
    video_id = response.json()['video_id']
    print(f"✅ Video uploaded successfully: {video_id}")
    
    # Step 4: Start processing
    print("\n⚙️  Starting video processing...")
    response = requests.post(f"{base_url}/api/videos/{video_id}/process", headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Processing start failed: {response.status_code} - {response.text}")
        return False
    
    job_id = response.json()['job_id']
    print(f"✅ Processing job started: {job_id}")
    
    # Step 5: Monitor processing with detailed status tracking
    print("\n🔄 Monitoring processing pipeline...")
    print("Expected stages: pending → transcribing → audio_analysis → video_analysis → nlp_analysis → scoring → completed")
    print("-" * 80)
    
    report_id = None
    previous_status = None
    
    for i in range(30):  # Monitor for up to 30 polls (90 seconds)
        response = requests.get(f"{base_url}/api/jobs/{job_id}/status", headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Status check failed: {response.status_code}")
            break
            
        job_data = response.json()
        status = job_data.get('status', 'unknown')
        progress = job_data.get('progress', 0)
        current_step = job_data.get('current_step', 'N/A')
        report_id = job_data.get('report_id')
        
        # Only print when status changes or every 5th poll
        if status != previous_status or i % 5 == 0:
            print(f"Poll {i+1:2d}: Status={status:15s} Progress={progress:3d}% Step={current_step}")
            previous_status = status
        
        if status == 'completed' and report_id:
            print(f"\n🎉 PROCESSING COMPLETED! Report ID: {report_id}")
            break
            
        elif status == 'failed':
            print(f"\n❌ Processing failed at: {current_step}")
            return False
            
        time.sleep(3)  # Wait 3 seconds between polls
    
    # Step 6: Test report retrieval if processing completed
    if report_id:
        print(f"\n📊 Testing report retrieval...")
        response = requests.get(f"{base_url}/api/reports/{report_id}", headers=headers)
        
        if response.status_code == 200:
            report = response.json()
            print("✅ Report retrieved successfully")
            
            # Verify all required fields
            required_fields = ['overall_score', 'gravitas_score', 'communication_score', 
                             'presence_score', 'storytelling_score', 'detailed_metrics', 'coaching_tips']
            
            print("\n📋 Report Field Verification:")
            all_fields_present = True
            for field in required_fields:
                if field in report:
                    value = report[field]
                    if field.endswith('_score'):
                        print(f"   ✅ {field}: {value}")
                    else:
                        print(f"   ✅ {field}: Present ({type(value).__name__})")
                else:
                    print(f"   ❌ {field}: Missing")
                    all_fields_present = False
            
            if all_fields_present:
                print("\n🎯 ALL REQUIRED REPORT FIELDS PRESENT")
                return True
            else:
                print("\n⚠️  Some required report fields are missing")
                return False
        else:
            print(f"❌ Report retrieval failed: {response.status_code}")
            return False
    else:
        print(f"\n⚠️  Processing did not complete within monitoring period")
        return False

def main():
    success = test_comprehensive_video_pipeline()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 COMPREHENSIVE VIDEO PIPELINE TEST: PASSED")
        print("✅ Video upload, processing, and report generation all working correctly")
    else:
        print("❌ COMPREHENSIVE VIDEO PIPELINE TEST: FAILED")
        print("⚠️  Check logs above for specific failure points")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())