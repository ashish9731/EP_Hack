from fastapi import APIRouter, HTTPException, Cookie, Header
from typing import Optional
from datetime import datetime, timezone
import uuid

from models.profile import ProfileCreateRequest, UserProfile
from utils.auth import get_current_user

def create_profile_router(supabase):
    router = APIRouter(prefix="/profile", tags=["profile"])
    
    @router.post("/")
    async def create_profile(
        request: ProfileCreateRequest,
        session_token: Optional[str] = Cookie(None),
        authorization: Optional[str] = Header(None)
    ):
        user = get_current_user(session_token, authorization)
        
        try:
            # Get Supabase client
            supabase_client = supabase()
            
            now = datetime.now(timezone.utc).isoformat()
            
            # Prepare profile data
            profile_data = {
                "id": user["user_id"],
                "first_name": request.first_name,
                "last_name": request.last_name,
                "company": request.company,
                "role": request.role,
                "industry": request.industry,
                "experience_level": request.experience_level,
                "communication_goals": request.communication_goals,
                "updated_at": now
            }
            
            # Save profile to Supabase
            response = supabase_client.table("profiles").upsert(profile_data).execute()
            
            return response.data[0] if response.data else profile_data
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create profile: {str(e)}")
    
    @router.get("/")
    async def get_profile(
        session_token: Optional[str] = Cookie(None),
        authorization: Optional[str] = Header(None)
    ):
        user = get_current_user(session_token, authorization)
        
        try:
            # Get Supabase client
            supabase_client = supabase()
            
            # Query profile from Supabase
            response = supabase_client.table("profiles").select("*").eq("id", user["user_id"]).execute()
            
            if not response.data:
                raise HTTPException(status_code=404, detail="Profile not found")
            
            return response.data[0]
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get profile: {str(e)}")
    
    return router