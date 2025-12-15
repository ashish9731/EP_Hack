from fastapi import APIRouter, HTTPException, Cookie, Header
from typing import Optional
from datetime import datetime, timezone
import uuid

from models.profile import ProfileCreateRequest, UserProfile
from utils.auth import get_current_user

# Mock storage for user profiles
user_profiles = {}

def create_profile_router(supabase):
    router = APIRouter(prefix="/profile", tags=["profile"])
    
    @router.post("/")
    async def create_profile(
        request: ProfileCreateRequest,
        session_token: Optional[str] = Cookie(None),
        authorization: Optional[str] = Header(None)
    ):
        user = get_current_user(session_token, authorization)
        
        # Check if profile exists
        existing_profile = user_profiles.get(user["user_id"])
        
        now = datetime.now(timezone.utc).isoformat()
        profile_data = {
            "id": str(uuid.uuid4()),
            "user_id": user["user_id"],
            "role": request.role,
            "seniority_level": request.seniority_level,
            "years_experience": request.years_experience,
            "industry": request.industry,
            "company_size": request.company_size,
            "primary_goal": request.primary_goal,
            "created_at": now,
            "updated_at": now
        }
        
        # Save profile
        user_profiles[user["user_id"]] = profile_data
        
        return profile_data
    
    @router.get("/")
    async def get_profile(
        session_token: Optional[str] = Cookie(None),
        authorization: Optional[str] = Header(None)
    ):
        user = get_current_user(session_token, authorization)
        
        profile = user_profiles.get(user["user_id"])
        
        if not profile:
            return {"has_profile": False}
        
        return {"has_profile": True, "profile": profile}
    
    return router