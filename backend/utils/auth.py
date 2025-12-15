import os
import uuid
import hashlib
import json
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException, Cookie, Header
from typing import Optional

# Simple in-memory storage for users and sessions (for demonstration only)
# In a real application, you would use a proper database
users_db = {}
sessions_db = {}

def hash_password(password: str) -> str:
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return hash_password(plain_password) == hashed_password

def create_user(email: str, password: str, name: str):
    """Create a new user"""
    if email in users_db:
        raise Exception("User already exists")
    
    user_id = str(uuid.uuid4())
    hashed_password = hash_password(password)
    
    user = {
        "id": user_id,
        "email": email,
        "name": name,
        "password": hashed_password,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    users_db[email] = user
    return user

def get_user_by_email(email: str):
    """Get a user by email"""
    return users_db.get(email)

def create_session_token(user_id: str) -> str:
    """Create a session token for the user"""
    session_token = f"session_{uuid.uuid4().hex}"
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    
    session_data = {
        "user_id": user_id,
        "session_token": session_token,
        "expires_at": expires_at.isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    sessions_db[session_token] = session_data
    return session_token

def get_current_user(session_token: Optional[str] = Cookie(None), authorization: Optional[str] = Header(None)):
    """Get the current authenticated user"""
    token = session_token
    
    if not token and authorization:
        if authorization.startswith("Bearer "):
            token = authorization.replace("Bearer ", "")
    
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Find session
    if token not in sessions_db:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    session_doc = sessions_db[token]
    
    # Check if session is expired
    expires_at = session_doc["expires_at"]
    if isinstance(expires_at, str):
        expires_at = datetime.fromisoformat(expires_at)
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    
    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Session expired")
    
    # Get user
    user_id = session_doc["user_id"]
    user = None
    for u in users_db.values():
        if u["id"] == user_id:
            user = u
            break
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Transform user to match existing structure
    return {
        "user_id": user["id"],
        "email": user["email"],
        "name": user["name"],
        "created_at": user["created_at"]
    }

def delete_session(session_token: str):
    """Delete a session"""
    if session_token in sessions_db:
        del sessions_db[session_token]