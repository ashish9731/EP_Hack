import os
import uuid
from datetime import datetime, timezone
from typing import Union
from fastapi import UploadFile
from utils.supabase_client import get_supabase_client
import logging

logger = logging.getLogger(__name__)

async def save_video_to_storage(file: UploadFile, user_id: str) -> str:
    """Save a video file to Supabase storage and return its ID"""
    try:
        # Get Supabase client
        supabase = get_supabase_client()
        
        # Generate unique video ID
        video_id = f"video_{uuid.uuid4().hex}"
        
        # Read file content
        content = await file.read()
        
        # Create file path - organize by user ID and date
        today = datetime.now(timezone.utc).strftime("%Y/%m/%d")
        file_path = f"videos/{user_id}/{today}/{video_id}_{file.filename}"
        
        # Upload to Supabase storage
        # Create or get the bucket
        bucket_name = "videos"
        
        # Upload the file
        response = supabase.storage.from_(bucket_name).upload(
            file_path, 
            content,
            file_options={"content-type": file.content_type}
        )
        
        logger.info(f"Video uploaded to Supabase storage: {file_path}")
        
        # Store metadata in database
        metadata = {
            "id": video_id,
            "user_id": user_id,
            "filename": file.filename,
            "file_path": file_path,
            "content_type": file.content_type,
            "size": len(content),
            "uploaded_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Insert metadata into videos table
        supabase.table("videos").insert(metadata).execute()
        
        return video_id
        
    except Exception as e:
        logger.error(f"Failed to save video to Supabase storage: {str(e)}", exc_info=True)
        raise Exception(f"Failed to save video: {str(e)}")

def get_video_from_storage(video_id: str) -> dict:
    """Retrieve a video file metadata from Supabase"""
    try:
        # Get Supabase client
        supabase = get_supabase_client()
        
        # Query video metadata from database
        response = supabase.table("videos").select("*").eq("id", video_id).execute()
        
        if not response.data:
            raise Exception(f"Video metadata not found: {video_id}")
        
        video_metadata = response.data[0]
        
        # Get the file from storage
        bucket_name = "videos"
        file_path = video_metadata["file_path"]
        
        # Get public URL for the file
        public_url = supabase.storage.from_(bucket_name).get_public_url(file_path)
        video_metadata["public_url"] = public_url
        
        return video_metadata
        
    except Exception as e:
        logger.error(f"Failed to retrieve video from Supabase storage: {str(e)}", exc_info=True)
        raise Exception(f"Failed to retrieve video: {str(e)}")

def delete_video_from_storage(video_id: str) -> bool:
    """Delete a video file from Supabase storage"""
    try:
        # Get Supabase client
        supabase = get_supabase_client()
        
        # First get the video metadata to get the file path
        response = supabase.table("videos").select("file_path").eq("id", video_id).execute()
        
        if not response.data:
            return False
            
        file_path = response.data[0]["file_path"]
        
        # Delete from storage
        bucket_name = "videos"
        supabase.storage.from_(bucket_name).remove([file_path])
        
        # Delete metadata from database
        supabase.table("videos").delete().eq("id", video_id).execute()
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to delete video from Supabase storage: {str(e)}", exc_info=True)
        return False

def get_signed_url(video_id: str, expires_in: int = 3600) -> str:
    """Get a signed URL for a video file that expires in specified seconds"""
    try:
        # Get Supabase client
        supabase = get_supabase_client()
        
        # Get video metadata
        response = supabase.table("videos").select("file_path").eq("id", video_id).execute()
        
        if not response.data:
            raise Exception(f"Video not found: {video_id}")
            
        file_path = response.data[0]["file_path"]
        
        # Generate signed URL
        bucket_name = "videos"
        signed_url = supabase.storage.from_(bucket_name).create_signed_url(file_path, expires_in)
        
        return signed_url.signed_url
        
    except Exception as e:
        logger.error(f"Failed to generate signed URL for video: {str(e)}", exc_info=True)
        raise Exception(f"Failed to generate signed URL: {str(e)}")