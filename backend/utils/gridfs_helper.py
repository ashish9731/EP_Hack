import os
import uuid
from datetime import datetime, timezone
from typing import Union
from fastapi import UploadFile

# Mock storage for video files
video_files = {}

async def save_video_to_storage(file: UploadFile) -> str:
    """Save a video file and return its ID"""
    video_id = f"video_{uuid.uuid4().hex}"
    
    # Read file content (in a real implementation, you would save this to disk or cloud storage)
    content = await file.read()
    
    # Store file info
    video_files[video_id] = {
        "id": video_id,
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(content),
        "content": content,
        "uploaded_at": datetime.now(timezone.utc).isoformat()
    }
    
    return video_id

def get_video_from_storage(video_id: str) -> dict:
    """Retrieve a video file by ID"""
    if video_id not in video_files:
        raise Exception(f"Video file not found: {video_id}")
    
    return video_files[video_id]

def delete_video_from_storage(video_id: str) -> bool:
    """Delete a video file by ID"""
    if video_id in video_files:
        del video_files[video_id]
        return True
    return False