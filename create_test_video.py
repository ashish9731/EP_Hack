#!/usr/bin/env python3

import subprocess
import os

def create_test_video():
    """Create a minimal test video file using ffmpeg"""
    output_file = "/tmp/test_video.mp4"
    
    # Create a 5-second test video with a simple pattern and audio tone
    command = [
        '/usr/bin/ffmpeg',
        '-f', 'lavfi',
        '-i', 'testsrc=duration=5:size=320x240:rate=1',  # Simple test pattern
        '-f', 'lavfi', 
        '-i', 'sine=frequency=1000:duration=5',  # 1kHz tone
        '-c:v', 'libx264',
        '-c:a', 'aac',
        '-shortest',
        '-y',  # Overwrite if exists
        output_file
    ]
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"✅ Test video created: {output_file}")
            print(f"File size: {os.path.getsize(output_file)} bytes")
            return output_file
        else:
            print(f"❌ Failed to create test video: {result.stderr}")
            return None
    except Exception as e:
        print(f"❌ Error creating test video: {e}")
        return None

if __name__ == "__main__":
    create_test_video()