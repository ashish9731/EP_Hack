from fastapi import APIRouter, HTTPException, Cookie, Header
from typing import Optional
from datetime import datetime, timezone
import uuid

from models.profile import ProfileCreateRequest, UserProfile
from utils.supabase_auth import get_current_user

def create_profile_router(supabase):
    router = APIRouter(prefix="/profile", tags=["profile"])
    
    @router.post("/")
    async def create_profile(
        request: ProfileCreateRequest,
        session_token: Optional[str] = Cookie(None),
        authorization: Optional[str] = Header(None)
    ):
        user = await get_current_user(session_token, authorization)
        
        # Check if profile exists
        try:
            profile_response = supabase.table("user_profiles").select("*").eq("user_id", user["user_id"]).execute()
            existing_profile = profile_response.data[0] if profile_response.data else None
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        
        now = datetime.now(timezone.utc).isoformat()
        profile_data = {
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
        
        try:
            if existing_profile:
                # Update existing profile
                supabase.table("user_profiles").update(profile_data).eq("user_id", user["user_id"]).execute()
            else:
                # Create new profile
                supabase.table("user_profiles").insert(profile_data).execute()
            
            # Get the updated/created profile
            profile_response = supabase.table("user_profiles").select("*").eq("user_id", user["user_id"]).execute()
            profile_doc = profile_response.data[0] if profile_response.data else profile_data
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save profile: {str(e)}")
        
        return profile_doc
    
    @router.get("/")
    async def get_profile(
        session_token: Optional[str] = Cookie(None),
        authorization: Optional[str] = Header(None)
    ):
        user = await get_current_user(session_token, authorization)
        
        try:
            profile_response = supabase.table("user_profiles").select("*").eq("user_id", user["user_id"]).execute()
            profile = profile_response.data[0] if profile_response.data else None
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        
        if not profile:
            return {"has_profile": False}
        
        return {"has_profile": True, "profile": profile}
    
    return router