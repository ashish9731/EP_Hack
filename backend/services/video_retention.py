"""
Video Retention Service
Handles secure video storage with configurable auto-delete functionality
"""
import os
import asyncio
from datetime import datetime, timezone, timedelta
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

# Mock storage for video metadata and user settings
video_metadata = {}
user_settings = {}

class VideoRetentionService:
    def __init__(self, supabase=None):
        self._cleanup_task = None
    
    async def set_video_retention(self, video_id: str, user_id: str, retention_period: str) -> dict:
        """Set retention policy for a specific video"""
        if retention_period not in RETENTION_PERIODS:
            raise ValueError(f"Invalid retention period. Choose from: {list(RETENTION_PERIODS.keys())}")
        
        days = RETENTION_PERIODS[retention_period]
        delete_at = None
        if days is not None:
            delete_at = (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()
        
        # Update video metadata
        if video_id in video_metadata:
            video_metadata[video_id].update({
                "retention_policy": retention_period,
                "scheduled_deletion": delete_at,
                "retention_updated_at": datetime.now(timezone.utc).isoformat()
            })
        
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
        
        # Check if user settings exist
        if user_id in user_settings:
            # Update existing settings
            user_settings[user_id].update({
                "default_retention": retention_period,
                "updated_at": datetime.now(timezone.utc).isoformat()
            })
        else:
            # Create new settings
            user_settings[user_id] = {
                "user_id": user_id,
                "default_retention": retention_period,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        
        return {
            "user_id": user_id,
            "default_retention": retention_period,
            "message": f"Default retention set to {retention_period}"
        }
    
    async def get_user_retention_settings(self, user_id: str) -> dict:
        """Get user's retention settings and video retention info"""
        settings = user_settings.get(user_id, {})
        videos = [v for v in video_metadata.values() if v.get("user_id") == user_id]
        
        return {
            "default_retention": settings.get("default_retention", "30_days") if settings else "30_days",
            "videos": videos,
            "available_policies": list(RETENTION_PERIODS.keys())
        }
    
    async def delete_video_now(self, video_id: str, user_id: str) -> dict:
        """Immediately delete a video and its associated data"""
        # Verify ownership
        video = video_metadata.get(video_id)
        if not video or video.get("user_id") != user_id:
            raise ValueError("Video not found or access denied")
        
        # Delete video file from storage
        try:
            from utils.gridfs_helper import delete_video_from_storage
            delete_video_from_storage(video_id)
        except Exception as e:
            logger.warning(f"Storage deletion failed for {video_id}: {e}")
        
        # Delete metadata
        if video_id in video_metadata:
            del video_metadata[video_id]
        
        logger.info(f"Video {video_id} deleted by user {user_id}")
        
        return {
            "video_id": video_id,
            "status": "deleted",
            "message": "Video and associated data have been permanently deleted"
        }
    
    async def cleanup_expired_videos(self) -> dict:
        """Background task to delete videos past their retention period"""
        now = datetime.now(timezone.utc)
        
        # Find expired videos
        expired = []
        for video_id, video in video_metadata.items():
            scheduled_deletion = video.get("scheduled_deletion")
            if scheduled_deletion:
                deletion_time = datetime.fromisoformat(scheduled_deletion)
                if deletion_time.tzinfo is None:
                    deletion_time = deletion_time.replace(tzinfo=timezone.utc)
                if deletion_time < now:
                    expired.append(video)
        
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
            "timestamp": now.isoformat()
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
        """Stop background cleanup task"""
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
            logger.info("Video cleanup scheduler stopped")

def create_retention_router(supabase):
    from fastapi import APIRouter, HTTPException, Cookie, Header
    from typing import Optional
    from utils.auth import get_current_user
    
    router = APIRouter(prefix="/retention", tags=["retention"])
    retention_service = VideoRetentionService()
    
    @router.get("/settings")
    async def get_settings(
        session_token: Optional[str] = Cookie(None),
        authorization: Optional[str] = Header(None)
    ):
        user = get_current_user(session_token, authorization)
        try:
            settings = await retention_service.get_user_retention_settings(user["user_id"])
            return settings
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.put("/settings/default")
    async def set_default_retention(
        payload: dict,
        session_token: Optional[str] = Cookie(None),
        authorization: Optional[str] = Header(None)
    ):
        user = get_current_user(session_token, authorization)
        retention_period = payload.get("retention_period")
        
        if not retention_period:
            raise HTTPException(status_code=400, detail="retention_period is required")
        
        try:
            result = await retention_service.set_user_default_retention(user["user_id"], retention_period)
            return result
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.put("/videos/{video_id}")
    async def set_video_retention(
        video_id: str,
        payload: dict,
        session_token: Optional[str] = Cookie(None),
        authorization: Optional[str] = Header(None)
    ):
        user = get_current_user(session_token, authorization)
        retention_period = payload.get("retention_period")
        
        if not retention_period:
            raise HTTPException(status_code=400, detail="retention_period is required")
        
        try:
            result = await retention_service.set_video_retention(video_id, user["user_id"], retention_period)
            return result
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.delete("/videos/{video_id}")
    async def delete_video(
        video_id: str,
        session_token: Optional[str] = Cookie(None),
        authorization: Optional[str] = Header(None)
    ):
        user = get_current_user(session_token, authorization)
        
        try:
            result = await retention_service.delete_video_now(video_id, user["user_id"])
            return result
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    return router