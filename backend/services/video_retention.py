"""
Video Retention Service
Handles secure video storage with configurable auto-delete functionality
"""
import os
import asyncio
from datetime import datetime, timezone, timedelta
from supabase import create_client, Client
import logging

logger = logging.getLogger(__name__)

# Default retention periods in days
RETENTION_PERIODS = {
    "7_days": 7,
    "30_days": 30,
    "90_days": 90,
    "1_year": 365,
    "permanent": None  # Never auto-delete
}

class VideoRetentionService:
    def __init__(self, supabase: Client):
        self.supabase = supabase
        self._cleanup_task = None
    
    async def set_video_retention(self, video_id: str, user_id: str, retention_period: str) -> dict:
        """Set retention policy for a specific video"""
        if retention_period not in RETENTION_PERIODS:
            raise ValueError(f"Invalid retention period. Choose from: {list(RETENTION_PERIODS.keys())}")
        
        days = RETENTION_PERIODS[retention_period]
        delete_at = None
        if days is not None:
            delete_at = (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()
        
        try:
            self.supabase.table("video_metadata").update(
                {
                    "retention_policy": retention_period,
                    "scheduled_deletion": delete_at,
                    "retention_updated_at": datetime.now(timezone.utc).isoformat()
                }
            ).eq("id", video_id).eq("user_id", user_id).execute()
        except Exception as e:
            raise Exception(f"Failed to update video retention: {str(e)}")
        
        return {
            "video_id": video_id,
            "retention_policy": retention_period,
            "scheduled_deletion": delete_at,
            "message": f"Video will be deleted {'never' if delete_at is None else f'on {delete_at[:10]}'}"
        }
    
    async def set_user_default_retention(self, user_id: str, retention_period: str) -> dict:
        """Set default retention policy for a user's future uploads"""
        if retention_period not in RETENTION_PERIODS:
            raise ValueError(f"Invalid retention period. Choose from: {list(RETENTION_PERIODS.keys())}")
        
        try:
            # Check if user settings exist
            settings_response = self.supabase.table("user_settings").select("*").eq("user_id", user_id).execute()
            
            if settings_response.data:
                # Update existing settings
                self.supabase.table("user_settings").update(
                    {
                        "default_retention": retention_period,
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }
                ).eq("user_id", user_id).execute()
            else:
                # Create new settings
                settings_data = {
                    "user_id": user_id,
                    "default_retention": retention_period,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
                self.supabase.table("user_settings").insert(settings_data).execute()
        except Exception as e:
            raise Exception(f"Failed to set user retention: {str(e)}")
        
        return {
            "user_id": user_id,
            "default_retention": retention_period,
            "message": f"Default retention set to {retention_period}"
        }
    
    async def get_user_retention_settings(self, user_id: str) -> dict:
        """Get user's retention settings and video retention info"""
        try:
            settings_response = self.supabase.table("user_settings").select("*").eq("user_id", user_id).execute()
            settings = settings_response.data[0] if settings_response.data else {}
            
            videos_response = self.supabase.table("video_metadata").select(
                "id,filename,retention_policy,scheduled_deletion,uploaded_at"
            ).eq("user_id", user_id).execute()
            videos = videos_response.data
        except Exception as e:
            raise Exception(f"Failed to retrieve retention settings: {str(e)}")
        
        return {
            "default_retention": settings.get("default_retention", "30_days") if settings else "30_days",
            "videos": videos,
            "available_policies": list(RETENTION_PERIODS.keys())
        }
    
    async def delete_video_now(self, video_id: str, user_id: str) -> dict:
        """Immediately delete a video and its associated data"""
        # Verify ownership
        try:
            metadata_response = self.supabase.table("video_metadata").select("*").eq("id", video_id).eq("user_id", user_id).execute()
            if not metadata_response.data:
                raise ValueError("Video not found or access denied")
        except Exception as e:
            raise Exception(f"Failed to verify video ownership: {str(e)}")
        
        # Delete video file from storage
        try:
            from utils.gridfs_helper import delete_video_from_storage
            await delete_video_from_storage(video_id)
        except Exception as e:
            logger.warning(f"Storage deletion failed for {video_id}: {e}")
        
        # Delete metadata
        try:
            self.supabase.table("video_metadata").delete().eq("id", video_id).execute()
        except Exception as e:
            logger.warning(f"Metadata deletion failed for {video_id}: {e}")
        
        # Delete associated jobs
        try:
            self.supabase.table("processing_jobs").delete().eq("video_id", video_id).execute()
        except Exception as e:
            logger.warning(f"Job deletion failed for {video_id}: {e}")
        
        # Note: Reports are kept for historical reference but video_id is nullified
        try:
            self.supabase.table("ep_reports").update(
                {
                    "video_id": None, 
                    "video_deleted": True, 
                    "video_deleted_at": datetime.now(timezone.utc).isoformat()
                }
            ).eq("video_id", video_id).execute()
        except Exception as e:
            logger.warning(f"Report update failed for {video_id}: {e}")
        
        logger.info(f"Video {video_id} deleted by user {user_id}")
        
        return {
            "video_id": video_id,
            "status": "deleted",
            "message": "Video and associated data have been permanently deleted"
        }
    
    async def cleanup_expired_videos(self) -> dict:
        """Background task to delete videos past their retention period"""
        now = datetime.now(timezone.utc).isoformat()
        
        # Find expired videos
        try:
            expired_response = self.supabase.table("video_metadata").select("*").lt("scheduled_deletion", now).not_.is_("scheduled_deletion", "null").execute()
            expired = expired_response.data
        except Exception as e:
            raise Exception(f"Failed to find expired videos: {str(e)}")
        
        deleted_count = 0
        errors = []
        
        for video in expired:
            try:
                await self.delete_video_now(video["id"], video["user_id"])
                deleted_count += 1
            except Exception as e:
                errors.append({"video_id": video["id"], "error": str(e)})
                logger.error(f"Failed to delete expired video {video['id']}: {e}")
        
        return {
            "deleted_count": deleted_count,
            "errors": errors,
            "timestamp": now
        }
    
    async def start_cleanup_scheduler(self, interval_hours: int = 24):
        """Start background cleanup task"""
        async def cleanup_loop():
            while True:
                try:
                    result = await self.cleanup_expired_videos()
                    logger.info(f"Cleanup completed: {result['deleted_count']} videos deleted")
                except Exception as e:
                    logger.error(f"Cleanup task failed: {e}")
                
                await asyncio.sleep(interval_hours * 3600)
        
        self._cleanup_task = asyncio.create_task(cleanup_loop())
        logger.info(f"Video cleanup scheduler started (interval: {interval_hours}h)")
    
    def stop_cleanup_scheduler(self):
        """Stop the cleanup background task"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            self._cleanup_task = None


def create_retention_router(supabase: Client):
    """Create FastAPI router for video retention endpoints"""
    from fastapi import APIRouter, HTTPException, Cookie, Header
    from typing import Optional
    from pydantic import BaseModel
    from utils.supabase_auth import get_current_user
    
    router = APIRouter(prefix="/retention", tags=["Video Retention"])
    retention_service = VideoRetentionService(supabase)
    
    class RetentionRequest(BaseModel):
        retention_period: str
    
    @router.get("/settings")
    async def get_retention_settings(
        session_token: Optional[str] = Cookie(None),
        authorization: Optional[str] = Header(None)
    ):
        """Get user's video retention settings"""
        try:
            user = await get_current_user(session_token, authorization)
            settings = await retention_service.get_user_retention_settings(user["user_id"])
            return settings
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/videos/{video_id}")
    async def set_video_retention(
        video_id: str,
        request: RetentionRequest,
        session_token: Optional[str] = Cookie(None),
        authorization: Optional[str] = Header(None)
    ):
        """Set retention policy for a specific video"""
        try:
            user = await get_current_user(session_token, authorization)
            result = await retention_service.set_video_retention(video_id, user["user_id"], request.retention_period)
            return result
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/default")
    async def set_user_default_retention(
        request: RetentionRequest,
        session_token: Optional[str] = Cookie(None),
        authorization: Optional[str] = Header(None)
    ):
        """Set default retention policy for user's future uploads"""
        try:
            user = await get_current_user(session_token, authorization)
            result = await retention_service.set_user_default_retention(user["user_id"], request.retention_period)
            return result
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.delete("/videos/{video_id}")
    async def delete_video_now(
        video_id: str,
        session_token: Optional[str] = Cookie(None),
        authorization: Optional[str] = Header(None)
    ):
        """Immediately delete a video"""
        try:
            user = await get_current_user(session_token, authorization)
            result = await retention_service.delete_video_now(video_id, user["user_id"])
            return result
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    return router, retention_service