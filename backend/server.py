import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))
sys.path.insert(0, str(backend_path.parent))

# Also add the current directory
sys.path.insert(0, os.getcwd())
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))

from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File, Depends, Response, Cookie, Header
from fastapi.responses import StreamingResponse, FileResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import logging
from datetime import datetime, timezone, timedelta
import uuid
import asyncio
from typing import Optional
import httpx

import sys
sys.path.append('/app/backend')

from models.user import UserCreate, User, LoginRequest, SignupRequest, AuthResponse
from models.video import JobStatus, VideoMetadata, EPReport
from models.profile import ProfileCreateRequest, UserProfile
from utils.supabase_auth import create_session_token, get_current_user, get_supabase_client
from utils.gridfs_helper import save_video_to_storage, get_video_from_storage
from services.video_processor import VideoProcessorService
from routes.profile import create_profile_router
from routes.subscription import get_subscription_routes
from services.timed_content import (
    get_current_simulator_scenarios, 
    get_current_training_modules, 
    get_current_daily_tip,
    TimedContentService
)

from routes.coaching import create_coaching_router
from routes.sharing import create_sharing_router
from services.video_retention import create_retention_router, VideoRetentionService

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Initialize Supabase client
supabase = get_supabase_client()

app = FastAPI()
api_router = APIRouter(prefix="/api")

video_processor = None

def get_video_processor():
    global video_processor
    if video_processor is None:
        video_processor = VideoProcessorService(supabase)
    return video_processor

@api_router.post("/auth/signup")
async def signup(request: SignupRequest, response: Response):
    # Check if user already exists
    try:
        user_response = supabase.table("users").select("*").eq("email", request.email).execute()
        if user_response.data:
            raise HTTPException(status_code=400, detail="Email already registered")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    user_id = f"user_{uuid.uuid4().hex[:12]}"
    # Note: In a real implementation, Supabase would handle password hashing
    
    user_data = {
        "id": user_id,
        "email": request.email,
        "name": request.name,
        "picture": None,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    try:
        response = supabase.table("users").insert(user_data).execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")
    
    session_token = await create_session_token(user_id)
    
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=True,
        samesite="none",
        path="/",
        max_age=7 * 24 * 60 * 60
    )
    
    # Get the created user
    try:
        user_response = supabase.table("users").select("*").eq("id", user_id).execute()
        user = user_response.data[0] if user_response.data else None
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve user: {str(e)}")
    
    return {"user": user, "session_token": session_token}

@api_router.post("/auth/login")
async def login(request: LoginRequest, response: Response):
    # In a real implementation, Supabase would handle authentication
    # This is a simplified version for demonstration
    try:
        user_response = supabase.table("users").select("*").eq("email", request.email).execute()
        if not user_response.data:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        user_doc = user_response.data[0]
        # Note: In a real implementation, password verification would be done by Supabase
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    session_token = await create_session_token(user_doc["id"])
    
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=True,
        samesite="none",
        path="/",
        max_age=7 * 24 * 60 * 60
    )
    
    user = {k: v for k, v in user_doc.items() if k != "password_hash"}
    
    return {"user": user, "session_token": session_token}

@api_router.get("/auth/google-redirect")
async def google_auth_redirect():
    redirect_url = f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/dashboard"
    auth_url = f"https://auth.emergentagent.com/?redirect={redirect_url}"
    return {"auth_url": auth_url}

@api_router.get("/auth/session")
async def exchange_session(session_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data",
            headers={"X-Session-ID": session_id}
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid session")
        
        data = response.json()
        
        # Check if user exists in Supabase
        try:
            user_response = supabase.table("users").select("*").eq("email", data["email"]).execute()
            
            if user_response.data:
                user_id = user_response.data[0]["id"]
                # Update existing user
                update_data = {
                    "name": data.get("name", user_response.data[0].get("name", "")),
                    "picture": data.get("picture", user_response.data[0].get("picture"))
                }
                supabase.table("users").update(update_data).eq("id", user_id).execute()
            else:
                # Create new user
                user_id = f"user_{uuid.uuid4().hex[:12]}"
                user_data = {
                    "id": user_id,
                    "email": data["email"],
                    "name": data.get("name", ""),
                    "picture": data.get("picture"),
                    "created_at": datetime.now(timezone.utc).isoformat()
                }
                supabase.table("users").insert(user_data).execute()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        
        session_token = data.get("session_token") or await create_session_token(user_id)
        
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        session_data = {
            "user_id": user_id,
            "session_token": session_token,
            "expires_at": expires_at.isoformat(),
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        try:
            # Upsert session data
            supabase.table("user_sessions").upsert(session_data).execute()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to store session: {str(e)}")
        
        # Get user data
        try:
            user_response = supabase.table("users").select("*").eq("id", user_id).execute()
            user = user_response.data[0] if user_response.data else None
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to retrieve user: {str(e)}")
        
        return {"user": user, "session_token": session_token}

@api_router.get("/auth/me")
async def get_me(session_token: Optional[str] = Cookie(None), authorization: Optional[str] = Header(None)):
    user = await get_current_user(session_token, authorization)
    return user

@api_router.post("/auth/logout")
async def logout(response: Response, session_token: Optional[str] = Cookie(None)):
    if session_token:
        try:
            supabase.table("user_sessions").delete().eq("session_token", session_token).execute()
            response.delete_cookie("session_token", path="/")
        except Exception as e:
            # Log error but still clear cookie
            logging.error(f"Failed to delete session: {str(e)}")
            response.delete_cookie("session_token", path="/")
    return {"message": "Logged out"}

@api_router.post("/videos/upload")
async def upload_video(
    file: UploadFile = File(...),
    session_token: Optional[str] = Cookie(None),
    authorization: Optional[str] = Header(None)
):
    user = await get_current_user(session_token, authorization)
    
    if file.size and file.size > 200 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Video size exceeds 200MB limit")
    
    # Save video to Supabase storage
    try:
        video_id = await save_video_to_storage(file)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save video: {str(e)}")
    
    # Store video metadata in Supabase
    metadata_data = {
        "id": video_id,
        "user_id": user["user_id"],
        "filename": file.filename,
        "file_size": file.size or 0,
        "format": file.content_type,
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
        "retention_policy": "30_days",
        "scheduled_deletion": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
    }
    
    try:
        # Check for user's default retention setting
        user_settings_response = supabase.table("user_settings").select("*").eq("user_id", user["user_id"]).execute()
        if user_settings_response.data:
            from services.video_retention import RETENTION_PERIODS
            user_settings = user_settings_response.data[0]
            if user_settings.get("default_retention"):
                policy = user_settings["default_retention"]
                days = RETENTION_PERIODS.get(policy)
                metadata_data["retention_policy"] = policy
                metadata_data["scheduled_deletion"] = (datetime.now(timezone.utc) + timedelta(days=days)).isoformat() if days else None
        
        # Insert metadata
        supabase.table("video_metadata").insert(metadata_data).execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to store video metadata: {str(e)}")
    
    return {"video_id": video_id, "message": "Video uploaded successfully"}

@api_router.post("/videos/{video_id}/process")
async def process_video(
    video_id: str,
    session_token: Optional[str] = Cookie(None),
    authorization: Optional[str] = Header(None)
):
    user = await get_current_user(session_token, authorization)
    
    # Get video metadata from Supabase
    try:
        metadata_response = supabase.table("video_metadata").select("*").eq("id", video_id).eq("user_id", user["user_id"]).execute()
        if not metadata_response.data:
            raise HTTPException(status_code=404, detail="Video not found")
        metadata = metadata_response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve video metadata: {str(e)}")
    
    job_id = f"job_{uuid.uuid4().hex}"
    
    job_data = {
        "id": job_id,
        "user_id": user["user_id"],
        "video_id": video_id,
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    try:
        # Store job data in Supabase
        supabase.table("processing_jobs").insert(job_data).execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create processing job: {str(e)}")
    
    # Trigger video processing asynchronously
    asyncio.create_task(process_video_async(job_id, video_id, user["user_id"]))
    
    return {"job_id": job_id, "message": "Video processing started"}

@api_router.get("/jobs/{job_id}/status")
async def get_job_status(
    job_id: str,
    session_token: Optional[str] = Cookie(None),
    authorization: Optional[str] = Header(None)
):
    user = await get_current_user(session_token, authorization)
    
    try:
        job_response = supabase.table("processing_jobs").select("*").eq("id", job_id).eq("user_id", user["user_id"]).execute()
        if not job_response.data:
            raise HTTPException(status_code=404, detail="Job not found")
        job = job_response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve job: {str(e)}")
    
    return job

@api_router.get("/reports/{report_id}")
async def get_report(
    report_id: str,
    session_token: Optional[str] = Cookie(None),
    authorization: Optional[str] = Header(None)
):
    user = await get_current_user(session_token, authorization)
    
    try:
        report_response = supabase.table("ep_reports").select("*").eq("id", report_id).eq("user_id", user["user_id"]).execute()
        if not report_response.data:
            raise HTTPException(status_code=404, detail="Report not found")
        report = report_response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve report: {str(e)}")
    
    return report

@api_router.get("/reports")
async def list_reports(
    session_token: Optional[str] = Cookie(None),
    authorization: Optional[str] = Header(None)
):
    user = await get_current_user(session_token, authorization)
    
    try:
        reports_response = supabase.table("ep_reports").select("*").eq("user_id", user["user_id"]).order("created_at", desc=True).limit(50).execute()
        reports = reports_response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve reports: {str(e)}")
    
    return reports

@api_router.get("/videos/{video_id}/stream")
async def stream_video(
    video_id: str,
    session_token: Optional[str] = Cookie(None),
    authorization: Optional[str] = Header(None)
):
    user = await get_current_user(session_token, authorization)
    
    # Check if video exists
    try:
        metadata_response = supabase.table("video_metadata").select("*").eq("id", video_id).eq("user_id", user["user_id"]).execute()
        if not metadata_response.data:
            raise HTTPException(status_code=404, detail="Video not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve video: {str(e)}")
    
    # For now, we'll return a placeholder response
    # In a real implementation, you would stream the actual video data
    return {"message": "Video streaming endpoint", "video_id": video_id}

# Add the rest of the routes
app.include_router(api_router)
app.include_router(create_profile_router(supabase))
app.include_router(get_subscription_routes(supabase))
app.include_router(create_coaching_router(supabase))
app.include_router(create_sharing_router(supabase))
app.include_router(create_retention_router(supabase))

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

@app.get("/")
async def root():
    return {"message": "Executive Presence Hack API"}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}

# Placeholder for async video processing function
async def process_video_async(job_id: str, video_id: str, user_id: str):
    """Placeholder for video processing - in a real implementation this would do the actual processing"""
    try:
        # Update job status to processing
        update_data = {
            "status": "processing",
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        supabase.table("processing_jobs").update(update_data).eq("id", job_id).execute()
        
        # Simulate processing delay
        await asyncio.sleep(2)
        
        # Update job status to completed
        update_data = {
            "status": "completed",
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        supabase.table("processing_jobs").update(update_data).eq("id", job_id).execute()
        
        # Create a sample report
        report_data = {
            "id": f"report_{uuid.uuid4().hex}",
            "user_id": user_id,
            "video_id": video_id,
            "job_id": job_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "content": {
                "executive_presence_score": 85,
                "feedback": "Great presentation skills demonstrated",
                "recommendations": ["Improve eye contact", "Work on posture"]
            }
        }
        supabase.table("ep_reports").insert(report_data).execute()
        
    except Exception as e:
        # Update job status to failed
        update_data = {
            "status": "failed",
            "error_message": str(e),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        supabase.table("processing_jobs").update(update_data).eq("id", job_id).execute()
        logging.error(f"Video processing failed for job {job_id}: {str(e)}")

@api_router.get("/learning/daily-tip")
async def get_daily_tip(
    session_token: Optional[str] = Cookie(None),
    authorization: Optional[str] = Header(None)
):
    user = await get_current_user(session_token, authorization)
    tip = await get_current_daily_tip()
    return tip

@api_router.get("/learning/ted-talks")
async def get_ted_talks(
    session_token: Optional[str] = Cookie(None),
    authorization: Optional[str] = Header(None)
):
    await get_current_user(session_token, authorization)
    # Mock TED talks data - in a real implementation this would come from an API
    ted_talks = [
        {
            "id": "1",
            "title": "How to speak so that people want to listen",
            "speaker": "Julian Treasure",
            "duration": "9:59",
            "views": "25M",
            "link": "https://www.ted.com/talks/julian_treasure_how_to_speak_so_that_people_want_to_listen"
        },
        {
            "id": "2",
            "title": "The power of vulnerability",
            "speaker": "Brené Brown",
            "duration": "20:00",
            "views": "50M",
            "link": "https://www.ted.com/talks/brene_brown_the_power_of_vulnerability"
        },
        {
            "id": "3",
            "title": "How great leaders inspire action",
            "speaker": "Simon Sinek",
            "duration": "18:04",
            "views": "40M",
            "link": "https://www.ted.com/talks/simon_sinek_how_great_leaders_inspire_action"
        }
    ]
    return ted_talks

@api_router.get("/training/modules")
async def get_training_modules(
    session_token: Optional[str] = Cookie(None),
    authorization: Optional[str] = Header(None)
):
    await get_current_user(session_token, authorization)
    # Return list of available training modules
    modules = [
        {"id": "strategic-pauses", "title": "Strategic Pauses", "duration": "3 min"},
        {"id": "lens-eye-contact", "title": "Lens Eye Contact", "duration": "4 min"},
        {"id": "decision-framing", "title": "Decision Framing", "duration": "5 min"},
        {"id": "vocal-variety", "title": "Vocal Variety", "duration": "4 min"},
        {"id": "storytelling-structure", "title": "Storytelling Structure", "duration": "6 min"},
        {"id": "commanding-openings", "title": "Commanding Openings", "duration": "3 min"}
    ]
    return modules

@api_router.get("/simulator/scenarios")
async def get_simulator_scenarios(
    session_token: Optional[str] = Cookie(None),
    authorization: Optional[str] = Header(None)
):
    await get_current_user(session_token, authorization)
    # Get current scenarios based on rotation period
    scenarios = await get_current_simulator_scenarios()
    return scenarios
