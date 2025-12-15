"""
Video Retention Service
Handles secure video storage with configurable auto-delete functionality
"""
import os
import asyncio
from datetime import datetime, timezone, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
from gridfs import GridFS
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
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self._cleanup_task = None
    
    async def set_video_retention(self, video_id: str, user_id: str, retention_period: str) -> dict:
        """Set retention policy for a specific video"""
        if retention_period not in RETENTION_PERIODS:
            raise ValueError(f"Invalid retention period. Choose from: {list(RETENTION_PERIODS.keys())}")
        
        days = RETENTION_PERIODS[retention_period]
        delete_at = None
        if days is not None:
            delete_at = (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()
        
        await self.db.video_metadata.update_one(
            {"video_id": video_id, "user_id": user_id},
            {
                "$set": {
                    "retention_policy": retention_period,
                    "scheduled_deletion": delete_at,
                    "retention_updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
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
        
        await self.db.user_settings.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "default_retention": retention_period,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            },
            upsert=True
        )
        
        return {
            "user_id": user_id,
            "default_retention": retention_period,
            "message": f"Default retention set to {retention_period}"
        }
    
    async def get_user_retention_settings(self, user_id: str) -> dict:
        """Get user's retention settings and video retention info"""
        settings = await self.db.user_settings.find_one(
            {"user_id": user_id},
            {"_id": 0}
        )
        
        videos = await self.db.video_metadata.find(
            {"user_id": user_id},
            {"_id": 0, "video_id": 1, "filename": 1, "retention_policy": 1, "scheduled_deletion": 1, "uploaded_at": 1}
        ).to_list(100)
        
        return {
            "default_retention": settings.get("default_retention", "30_days") if settings else "30_days",
            "videos": videos,
            "available_policies": list(RETENTION_PERIODS.keys())
        }
    
    async def delete_video_now(self, video_id: str, user_id: str) -> dict:
        """Immediately delete a video and its associated data"""
        # Verify ownership
        metadata = await self.db.video_metadata.find_one(
            {"video_id": video_id, "user_id": user_id}
        )
        if not metadata:
            raise ValueError("Video not found or access denied")
        
        # Delete from GridFS
        try:
            from gridfs import GridFS
            from bson import ObjectId
            sync_db = self.db.delegate
            fs = GridFS(sync_db)
            fs.delete(ObjectId(video_id))
        except Exception as e:
            logger.warning(f"GridFS deletion failed for {video_id}: {e}")
        
        # Delete metadata
        await self.db.video_metadata.delete_one({"video_id": video_id})
        
        # Delete associated jobs
        await self.db.video_jobs.delete_many({"video_id": video_id})
        
        # Note: Reports are kept for historical reference but video_id is nullified
        await self.db.reports.update_many(
            {"video_id": video_id},
            {"$set": {"video_id": None, "video_deleted": True, "video_deleted_at": datetime.now(timezone.utc).isoformat()}}
        )
        
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
        expired = await self.db.video_metadata.find({
            "scheduled_deletion": {"$ne": None, "$lte": now}
        }).to_list(100)
        
        deleted_count = 0
        errors = []
        
        for video in expired:
            try:
                await self.delete_video_now(video["video_id"], video["user_id"])
                deleted_count += 1
            except Exception as e:
                errors.append({"video_id": video["video_id"], "error": str(e)})
                logger.error(f"Failed to delete expired video {video['video_id']}: {e}")
        
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


def create_retention_router(db: AsyncIOMotorDatabase):
    """Create FastAPI router for video retention endpoints"""
    from fastapi import APIRouter, HTTPException, Cookie, Header
    from typing import Optional
    from pydantic import BaseModel
    
    router = APIRouter(prefix="/retention", tags=["Video Retention"])
    retention_service = VideoRetentionService(db)
    
    class RetentionRequest(BaseModel):
        retention_period: str
    
    @router.get("/settings")
    async def get_retention_settings(
        session_token: Optional[str] = Cookie(None),
        authorization: Optional[str] = Header(None)
    ):
        """Get user's video retention settings"""
        from utils.auth import get_current_user
        user = await get_current_user(db, session_token, authorization)
        return await retention_service.get_user_retention_settings(user["user_id"])
    
    @router.put("/settings/default")
    async def set_default_retention(
        request: RetentionRequest,
        session_token: Optional[str] = Cookie(None),
        authorization: Optional[str] = Header(None)
    ):
        """Set default retention policy for future uploads"""
        from utils.auth import get_current_user
        user = await get_current_user(db, session_token, authorization)
        try:
            return await retention_service.set_user_default_retention(user["user_id"], request.retention_period)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    @router.put("/videos/{video_id}")
    async def set_video_retention(
        video_id: str,
        request: RetentionRequest,
        session_token: Optional[str] = Cookie(None),
        authorization: Optional[str] = Header(None)
    ):
        """Set retention policy for a specific video"""
        from utils.auth import get_current_user
        user = await get_current_user(db, session_token, authorization)
        try:
            return await retention_service.set_video_retention(video_id, user["user_id"], request.retention_period)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    @router.delete("/videos/{video_id}")
    async def delete_video(
        video_id: str,
        session_token: Optional[str] = Cookie(None),
        authorization: Optional[str] = Header(None)
    ):
        """Immediately delete a video"""
        from utils.auth import get_current_user
        user = await get_current_user(db, session_token, authorization)
        try:
            return await retention_service.delete_video_now(video_id, user["user_id"])
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
    
    return router, retention_service
