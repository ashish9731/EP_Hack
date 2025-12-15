#!/usr/bin/env python3

import requests
import time
import json

def test_video_pipeline():
    base_url = "https://exec-presence.preview.emergentagent.com"
    session_token = "session_715dbc2d083042dba4122d189f6b55e4"
    
    headers = {
        'Authorization': f'Bearer {session_token}',
        'Content-Type': 'application/json'
    }
    
    print("🎬 Testing Video Processing Pipeline")
    print("=" * 50)
    
    # Step 1: Login first
    login_data = {
        "email": "uitest_golden@test.com",
        "password": "TestPass123!"
    }
    
    response = requests.post(f"{base_url}/api/auth/login", json=login_data)
    if response.status_code == 200:
        session_token = response.json()['session_token']
        headers['Authorization'] = f'Bearer {session_token}'
        print("✅ Login successful")
    else:
        print("❌ Login failed")
        return
    
    # Step 2: Upload video
    dummy_content = b"dummy video content for testing - this is a longer test file to simulate real video"
    files = {
        'file': ('test_video.mp4', dummy_content, 'video/mp4')
    }
    
    upload_headers = {'Authorization': f'Bearer {session_token}'}
    response = requests.post(f"{base_url}/api/videos/upload", files=files, headers=upload_headers)
    
    if response.status_code != 200:
        print(f"❌ Video upload failed: {response.status_code} - {response.text}")
        return
    
    video_id = response.json()['video_id']
    print(f"✅ Video uploaded: {video_id}")
    
    # Step 3: Start processing
    response = requests.post(f"{base_url}/api/videos/{video_id}/process", headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Processing start failed: {response.status_code} - {response.text}")
        return
    
    job_id = response.json()['job_id']
    print(f"✅ Processing started: {job_id}")
    
    # Step 4: Monitor status
    print("\n🔄 Monitoring job status...")
    for i in range(15):  # Monitor for up to 15 polls
        response = requests.get(f"{base_url}/api/jobs/{job_id}/status", headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Status check failed: {response.status_code}")
            break
            
        job_data = response.json()
        status = job_data.get('status', 'unknown')
        progress = job_data.get('progress', 0)
        current_step = job_data.get('current_step', 'N/A')
        report_id = job_data.get('report_id')
        
        print(f"Poll {i+1}: Status={status}, Progress={progress}%, Step={current_step}")
        
        if status == 'completed' and report_id:
            print(f"🎉 Processing completed! Report ID: {report_id}")
            
            # Test report retrieval
            response = requests.get(f"{base_url}/api/reports/{report_id}", headers=headers)
            if response.status_code == 200:
                report = response.json()
                print("✅ Report retrieved successfully")
                print(f"   Overall Score: {report.get('overall_score', 'N/A')}")
                print(f"   Gravitas Score: {report.get('gravitas_score', 'N/A')}")
                print(f"   Communication Score: {report.get('communication_score', 'N/A')}")
                print(f"   Presence Score: {report.get('presence_score', 'N/A')}")
                print(f"   Storytelling Score: {report.get('storytelling_score', 'N/A')}")
            else:
                print(f"❌ Report retrieval failed: {response.status_code}")
            break
            
        elif status == 'failed':
            print(f"❌ Processing failed at step: {current_step}")
            break
            
        time.sleep(3)  # Wait 3 seconds between polls
    
    print("\n📊 Video Pipeline Test Complete")

if __name__ == "__main__":
    test_video_pipeline()