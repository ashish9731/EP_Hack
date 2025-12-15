from fastapi import APIRouter, HTTPException, Cookie, Header
from typing import Optional
from datetime import datetime, timezone
import uuid

from models.profile import ProfileCreateRequest, UserProfile
from utils.auth import get_current_user

def create_profile_router(db):
    router = APIRouter(prefix="/profile", tags=["profile"])
    
    @router.post("/")
    async def create_profile(
        request: ProfileCreateRequest,
        session_token: Optional[str] = Cookie(None),
        authorization: Optional[str] = Header(None)
    ):
        user = await get_current_user(db, session_token, authorization)
        
        existing_profile = await db.user_profiles.find_one({"user_id": user["user_id"]}, {"_id": 0})
        
        now = datetime.now(timezone.utc).isoformat()
        profile_doc = {
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
        
        if existing_profile:
            await db.user_profiles.update_one(
                {"user_id": user["user_id"]},
                {"$set": profile_doc}
            )
        else:
            await db.user_profiles.insert_one(profile_doc)
        
        return profile_doc
    
    @router.get("/")
    async def get_profile(
        session_token: Optional[str] = Cookie(None),
        authorization: Optional[str] = Header(None)
    ):
        user = await get_current_user(db, session_token, authorization)
        
        profile = await db.user_profiles.find_one({"user_id": user["user_id"]}, {"_id": 0})
        
        if not profile:
            return {"has_profile": False}
        
        return {"has_profile": True, "profile": profile}
    
    return router