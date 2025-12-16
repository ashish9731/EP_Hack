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

class VideoRetentionService:
    def __init__(self, supabase=None):
        self.supabase = supabase
        self._cleanup_task = None
    
    async def set_video_retention(self, video_id: str, user_id: str, retention_period: str) -> dict:
        """Set retention policy for a specific video"""
        if retention_period not in RETENTION_PERIODS:
            raise ValueError(f"Invalid retention period. Choose from: {list(RETENTION_PERIODS.keys())}")
        
        try:
            supabase_client = self.supabase()
            days = RETENTION_PERIODS[retention_period]
            delete_at = None
            if days is not None:
                delete_at = (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()
            
            # Update video metadata in Supabase
            update_data = {
                "retention_policy": retention_period,
                "scheduled_deletion": delete_at
            }
            
            response = supabase_client.table("videos").update(update_data).eq("id", video_id).eq("user_id", user_id).execute()
            
            if not response.data:
                raise Exception("Video not found or not owned by user")
            
            return {
                "video_id": video_id,
                "retention_policy": retention_period,
                "scheduled_deletion": delete_at
            }
            
        except Exception as e:
            logger.error(f"Failed to set video retention: {str(e)}")
            raise Exception(f"Failed to set video retention: {str(e)}")
    
    async def get_user_retention_settings(self, user_id: str) -> dict:
        """Get user's retention settings"""
        try:
            supabase_client = self.supabase()
            
            # Get user's videos with retention info
            response = supabase_client.table("videos").select("id,filename,uploaded_at,retention_policy,scheduled_deletion").eq("user_id", user_id).execute()
            
            videos = response.data if response.data else []
            
            # Get user's default retention setting (could be stored in a user_settings table)
            # For now, we'll use a default value
            default_retention = "30_days"
            
            return {
                "default_retention": default_retention,
                "videos": videos,
                "available_policies": list(RETENTION_PERIODS.keys())
            }
            
        except Exception as e:
            logger.error(f"Failed to get user retention settings: {str(e)}")
            raise Exception(f"Failed to get user retention settings: {str(e)}")
    
    async def set_default_retention(self, user_id: str, retention_period: str) -> dict:
        """Set default retention period for user"""
        if retention_period not in RETENTION_PERIODS:
            raise ValueError(f"Invalid retention period. Choose from: {list(RETENTION_PERIODS.keys())}")
        
        try:
            # In a real implementation, you would store this in a user_settings table
            # For now, we'll just return the setting
            return {
                "user_id": user_id,
                "default_retention": retention_period
            }
            
        except Exception as e:
            logger.error(f"Failed to set default retention: {str(e)}")
            raise Exception(f"Failed to set default retention: {str(e)}")

def create_retention_router(supabase):
    from fastapi import APIRouter, HTTPException, Cookie, Header
    from typing import Optional
    from utils.auth import get_current_user
    from pydantic import BaseModel
    
    router = APIRouter(prefix="/retention", tags=["retention"])
    retention_service = VideoRetentionService(supabase)
    
    class RetentionPolicyUpdate(BaseModel):
        retention_period: str
    
    @router.get("/settings")
    async def get_retention_settings(
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
    async def update_default_retention(
        request: RetentionPolicyUpdate,
        session_token: Optional[str] = Cookie(None),
        authorization: Optional[str] = Header(None)
    ):
        user = get_current_user(session_token, authorization)
        
        try:
            result = await retention_service.set_default_retention(user["user_id"], request.retention_period)
            return result
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.put("/videos/{video_id}")
    async def update_video_retention(
        video_id: str,
        request: RetentionPolicyUpdate,
        session_token: Optional[str] = Cookie(None),
        authorization: Optional[str] = Header(None)
    ):
        user = get_current_user(session_token, authorization)
        
        try:
            result = await retention_service.set_video_retention(video_id, user["user_id"], request.retention_period)
            return result
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    return router