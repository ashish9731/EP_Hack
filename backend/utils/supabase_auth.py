import os
import uuid
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException, Cookie, Header
from typing import Optional
from supabase import create_client, Client
import logging

logger = logging.getLogger(__name__)


def get_supabase_client() -> Client:
    """Initialize and return a Supabase client"""
    logger.debug("Initializing Supabase client")
    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get("SUPABASE_KEY")
    
    logger.debug(f"Supabase URL from env: {url}")
    logger.debug(f"Supabase KEY from env: {'*' * len(key) if key else None}")
    
    if not url or not key:
        logger.error("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
    
    try:
        client = create_client(url, key)
        logger.debug("Supabase client initialized successfully")
        return client
    except Exception as e:
        logger.error(f"Failed to initialize Supabase client: {str(e)}", exc_info=True)
        raise ValueError(f"Failed to initialize Supabase client: {str(e)}")


async def create_session_token(user_id: str) -> str:
    """Create a session token for the user"""
    logger.debug(f"Creating session token for user_id: {user_id}")
    
    try:
        supabase = get_supabase_client()
        session_token = f"session_{uuid.uuid4().hex}"
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        
        session_data = {
            "user_id": user_id,
            "session_token": session_token,
            "expires_at": expires_at.isoformat(),
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        logger.debug(f"Session data to insert: {session_data}")
        
        # Store session in Supabase
        response = supabase.table("user_sessions").insert(session_data).execute()
        logger.debug(f"Session insert response: {response}")
        
        logger.debug(f"Successfully created session token: {session_token}")
        return session_token
    except Exception as e:
        logger.error(f"Failed to create session for user {user_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")


async def get_current_user(session_token: Optional[str] = Cookie(None), authorization: Optional[str] = Header(None)):
    """Get the current authenticated user"""
    logger.debug(f"get_current_user called with session_token: {session_token}, authorization: {authorization}")
    
    token = session_token
    
    if not token and authorization:
        if authorization.startswith("Bearer "):
            token = authorization.replace("Bearer ", "")
            logger.debug(f"Extracted token from Authorization header: {token}")
    
    if not token:
        logger.warning("No authentication token provided")
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        # Get Supabase client
        logger.debug("Initializing Supabase client for user authentication")
        supabase = get_supabase_client()
        logger.debug("Supabase client initialized successfully")
        
        # Find session in Supabase
        logger.debug(f"Querying user_sessions table for token: {token}")
        response = supabase.table("user_sessions").select("*").eq("session_token", token).execute()
        logger.debug(f"Session query response: {response}")
        
        if not response.data:
            logger.warning(f"No session found for token: {token}")
            raise HTTPException(status_code=401, detail="Invalid session")
        
        session_doc = response.data[0]
        logger.debug(f"Found session document: {session_doc}")
        
        expires_at = session_doc["expires_at"]
        if isinstance(expires_at, str):
            expires_at = datetime.fromisoformat(expires_at)
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        
        if expires_at < datetime.now(timezone.utc):
            logger.warning(f"Session expired for token: {token}")
            raise HTTPException(status_code=401, detail="Session expired")
        
        # Get user from Supabase
        logger.debug(f"Querying users table for user_id: {session_doc['user_id']}")
        user_response = supabase.table("users").select("*").eq("id", session_doc["user_id"]).execute()
        logger.debug(f"User query response: {user_response}")
        
        if not user_response.data:
            logger.warning(f"User not found for user_id: {session_doc['user_id']}")
            raise HTTPException(status_code=404, detail="User not found")
        
        user_doc = user_response.data[0]
        logger.debug(f"Found user document: {user_doc}")
        
        # Transform Supabase user to match existing structure
        user = {
            "user_id": user_doc["id"],
            "email": user_doc["email"],
            "name": user_doc.get("name", ""),
            "picture": user_doc.get("picture"),
            "created_at": user_doc.get("created_at")
        }
        logger.debug(f"Returning user data: {user}")
        
        return user
    except HTTPException:
        # Re-raise HTTP exceptions
        logger.debug("Re-raising HTTPException")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_current_user: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Authentication error: {str(e)}")


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