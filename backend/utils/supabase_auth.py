import os
import uuid
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException, Cookie, Header
from typing import Optional
from supabase import create_client, Client


def get_supabase_client() -> Client:
    """Initialize and return a Supabase client"""
    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get("SUPABASE_KEY")
    
    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
    
    return create_client(url, key)


async def create_session_token(user_id: str) -> str:
    """Create a session token for the user"""
    supabase = get_supabase_client()
    session_token = f"session_{uuid.uuid4().hex}"
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    
    session_data = {
        "user_id": user_id,
        "session_token": session_token,
        "expires_at": expires_at.isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Store session in Supabase
    try:
        response = supabase.table("user_sessions").insert(session_data).execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")
    
    return session_token


async def get_current_user(session_token: Optional[str] = Cookie(None), authorization: Optional[str] = Header(None)):
    """Get the current authenticated user"""
    token = session_token
    
    if not token and authorization:
        if authorization.startswith("Bearer "):
            token = authorization.replace("Bearer ", "")
    
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Get Supabase client
    supabase = get_supabase_client()
    
    # Find session in Supabase
    try:
        response = supabase.table("user_sessions").select("*").eq("session_token", token).execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to query sessions: {str(e)}")
    
    if not response.data:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    session_doc = response.data[0]
    
    expires_at = session_doc["expires_at"]
    if isinstance(expires_at, str):
        expires_at = datetime.fromisoformat(expires_at)
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    
    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Session expired")
    
    # Get user from Supabase
    try:
        user_response = supabase.table("users").select("*").eq("id", session_doc["user_id"]).execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to query users: {str(e)}")
    
    if not user_response.data:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_doc = user_response.data[0]
    
    # Transform Supabase user to match existing structure
    user = {
        "user_id": user_doc["id"],
        "email": user_doc["email"],
        "name": user_doc.get("name", ""),
        "picture": user_doc.get("picture"),
        "created_at": user_doc.get("created_at")
    }
    
    return user


# These functions are kept for compatibility but won't be used with Supabase Auth
# Supabase handles password hashing and verification automatically through its auth system
async def hash_password(password: str) -> str:
    """Hash a password - in Supabase this is typically handled by the service"""
    # Note: Supabase handles password hashing automatically
    # This is kept for compatibility with existing code structure
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password - in Supabase this is typically handled by the service"""
    # Note: Supabase handles password verification automatically
    # This is kept for compatibility with existing code structure
    import hashlib
    return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password