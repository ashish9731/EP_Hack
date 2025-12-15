import os
import uuid
from fastapi import UploadFile
from supabase import create_client, Client

def get_supabase_client() -> Client:
    """Initialize and return a Supabase client"""
    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get("SUPABASE_KEY")
    
    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
    
    return create_client(url, key)

async def save_video_to_storage(file: UploadFile) -> str:
    """Save video file to Supabase storage and return video ID"""
    supabase = get_supabase_client()
    video_id = f"video_{uuid.uuid4().hex}"
    
    # Read file data
    file_data = await file.read()
    
    try:
        # Save file to Supabase storage
        # Note: This is a simplified implementation. In a real application,
        # you would use Supabase Storage properly with buckets
        supabase.table("video_files").insert({
            "id": video_id,
            "filename": file.filename,
            "content_type": file.content_type,
            "data": file_data,
            "size": len(file_data),
            "created_at": "now()"
        }).execute()
    except Exception as e:
        raise Exception(f"Failed to save video to storage: {str(e)}")
    
    return video_id

async def get_video_from_storage(video_id: str) -> bytes:
    """Retrieve video file from Supabase storage"""
    supabase = get_supabase_client()
    
    try:
        # Retrieve file from Supabase storage
        response = supabase.table("video_files").select("data").eq("id", video_id).execute()
        if not response.data:
            raise Exception("Video not found")
        
        video_data = response.data[0]["data"]
        return video_data
    except Exception as e:
        raise Exception(f"Failed to retrieve video from storage: {str(e)}")

async def delete_video_from_storage(video_id: str):
    """Delete video file from Supabase storage"""
    supabase = get_supabase_client()
    
    try:
        # Delete file from Supabase storage
        supabase.table("video_files").delete().eq("id", video_id).execute()
    except Exception as e:
        raise Exception(f"Failed to delete video from storage: {str(e)}")