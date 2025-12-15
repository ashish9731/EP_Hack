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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from models.user import UserCreate, User, LoginRequest, SignupRequest, AuthResponse
from models.video import JobStatus, VideoMetadata, EPReport
from models.profile import ProfileCreateRequest, UserProfile
from utils.auth import create_session_token, get_current_user, create_user, get_user_by_email, verify_password, delete_session
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

app = FastAPI()
api_router = APIRouter(prefix="/api")

video_processor = None

def get_video_processor():
    global video_processor
    if video_processor is None:
        # For now, we'll create a mock video processor
        class MockVideoProcessor:
            def process_video(self, video_path, user_id):
                # Mock implementation
                return {
                    "executive_presence_score": 85,
                    "feedback": "Good presentation skills",
                    "recommendations": ["Improve eye contact", "Work on posture"]
                }
        video_processor = MockVideoProcessor()
    return video_processor

@api_router.post("/auth/signup")
async def signup(request: SignupRequest, response: Response):
    logger.info(f"Signup attempt for email: {request.email}")
    
    try:
        # Create a new user
        user = create_user(request.email, request.password, request.name)
        logger.info(f"User created successfully: {user['id']}")
        
        # Create session token
        session_token = create_session_token(user["id"])
        logger.info(f"Session token created: {session_token}")
        
        # Set cookie
        is_production = not os.getenv("DEV_MODE", "false").lower() == "true"
        response.set_cookie(
            key="session_token",
            value=session_token,
            httponly=True,
            secure=is_production,
            samesite="lax" if not is_production else "none",
            path="/",
            max_age=7 * 24 * 60 * 60
        )
        
        # Transform user data to match existing structure
        user_response = {
            "user_id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "created_at": user["created_at"]
        }
        
        logger.info(f"Returning user data: {user_response}")
        return {"user": user_response, "session_token": session_token}
        
    except Exception as e:
        logger.error(f"Signup error: {str(e)}", exc_info=True)
        if "already exists" in str(e):
            raise HTTPException(status_code=400, detail="Email already registered")
        else:
            raise HTTPException(status_code=500, detail=f"Signup error: {str(e)}")

@api_router.post("/auth/login")
async def login(request: LoginRequest, response: Response):
    logger.info(f"Login attempt for email: {request.email}")
    
    try:
        # Get user by email
        user = get_user_by_email(request.email)
        if not user:
            logger.warning(f"User not found: {request.email}")
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Verify password
        if not verify_password(request.password, user["password"]):
            logger.warning(f"Invalid password for user: {request.email}")
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Create session token
        session_token = create_session_token(user["id"])
        logger.info(f"Session token created: {session_token}")
        
        # Set cookie
        is_production = not os.getenv("DEV_MODE", "false").lower() == "true"
        response.set_cookie(
            key="session_token",
            value=session_token,
            httponly=True,
            secure=is_production,
            samesite="lax" if not is_production else "none",
            path="/",
            max_age=7 * 24 * 60 * 60
        )
        
        # Transform user data to match existing structure
        user_response = {
            "user_id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "created_at": user["created_at"]
        }
        
        logger.info(f"Returning user data: {user_response}")
        return {"user": user_response, "session_token": session_token}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Authentication error: {str(e)}")

@api_router.get("/auth/google-redirect")
async def google_auth_redirect():
    logger.info("Google auth redirect requested")
    # For now, we'll just return a mock URL
    redirect_url = f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/dashboard"
    auth_url = f"{redirect_url}?mock_auth=true"
    logger.info(f"Generated mock auth URL: {auth_url}")
    return {"auth_url": auth_url}

@api_router.get("/auth/me")
async def get_me(session_token: Optional[str] = Cookie(None), authorization: Optional[str] = Header(None)):
    user = get_current_user(session_token, authorization)
    return user

@api_router.post("/auth/logout")
async def logout(response: Response, session_token: Optional[str] = Cookie(None)):
    if session_token:
        delete_session(session_token)
        
        # Determine if we should use secure cookies (True in production, False in development)
        is_production = not os.getenv("DEV_MODE", "false").lower() == "true"
        
        # Clear the cookie with the appropriate settings
        response.delete_cookie(
            "session_token",
            path="/",
            secure=is_production,
            samesite="lax" if not is_production else "none"
        )
    return {"message": "Logged out"}

@api_router.post("/videos/upload")
async def upload_video(
    file: UploadFile = File(...),
    session_token: Optional[str] = Cookie(None),
    authorization: Optional[str] = Header(None)
):
    user = get_current_user(session_token, authorization)
    
    if file.size and file.size > 200 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Video size exceeds 200MB limit")
    
    # Save video to storage (mock implementation)
    try:
        video_id = f"video_{uuid.uuid4().hex}"
        logger.info(f"Video uploaded successfully: {video_id}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save video: {str(e)}")
    
    # Store video metadata
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
    
    logger.info(f"Video metadata stored: {metadata_data}")
    
    return {"video_id": video_id, "message": "Video uploaded successfully"}

@api_router.post("/videos/{video_id}/process")
async def process_video(
    video_id: str,
    session_token: Optional[str] = Cookie(None),
    authorization: Optional[str] = Header(None)
):
    user = get_current_user(session_token, authorization)
    
    # Mock video processing
    job_id = f"job_{uuid.uuid4().hex}"
    
    job_data = {
        "id": job_id,
        "user_id": user["user_id"],
        "video_id": video_id,
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    logger.info(f"Processing job created: {job_data}")
    
    # Trigger video processing asynchronously
    asyncio.create_task(process_video_async(job_id, video_id, user["user_id"]))
    
    return {"job_id": job_id, "message": "Video processing started"}

@api_router.get("/jobs/{job_id}/status")
async def get_job_status(
    job_id: str,
    session_token: Optional[str] = Cookie(None),
    authorization: Optional[str] = Header(None)
):
    user = get_current_user(session_token, authorization)
    
    # Mock job status
    job = {
        "id": job_id,
        "user_id": user["user_id"],
        "status": "completed",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    logger.info(f"Returning job status: {job}")
    return job

@api_router.get("/reports/{report_id}")
async def get_report(
    report_id: str,
    session_token: Optional[str] = Cookie(None),
    authorization: Optional[str] = Header(None)
):
    user = get_current_user(session_token, authorization)
    
    # Mock report
    report = {
        "id": report_id,
        "user_id": user["user_id"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "content": {
            "executive_presence_score": 85,
            "feedback": "Great presentation skills demonstrated",
            "recommendations": ["Improve eye contact", "Work on posture"]
        }
    }
    
    logger.info(f"Returning report: {report}")
    return report

@api_router.get("/reports")
async def list_reports(
    session_token: Optional[str] = Cookie(None),
    authorization: Optional[str] = Header(None)
):
    user = get_current_user(session_token, authorization)
    
    # Mock reports list
    reports = [
        {
            "id": f"report_{uuid.uuid4().hex}",
            "user_id": user["user_id"],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "content": {
                "executive_presence_score": 85,
                "feedback": "Good presentation skills",
                "recommendations": ["Improve eye contact", "Work on posture"]
            }
        }
    ]
    
    logger.info(f"Returning reports list with {len(reports)} items")
    return reports

@api_router.get("/videos/{video_id}/stream")
async def stream_video(
    video_id: str,
    session_token: Optional[str] = Cookie(None),
    authorization: Optional[str] = Header(None)
):
    user = get_current_user(session_token, authorization)
    
    # Mock video streaming
    logger.info(f"Streaming video: {video_id}")
    return {"message": "Video streaming endpoint", "video_id": video_id}

# Add the rest of the routes
app.include_router(api_router)
app.include_router(create_profile_router(lambda: None))  # Mock database client
app.include_router(get_subscription_routes(lambda: None))  # Mock database client
app.include_router(create_coaching_router(lambda: None))  # Mock database client
app.include_router(create_sharing_router(lambda: None))  # Mock database client
app.include_router(create_retention_router(lambda: None))  # Mock database client

# CORS middleware
# Get frontend URL from environment variable, fallback to localhost for development
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
allowed_origins = [frontend_url]

# Add Vercel deployment URLs for production
if "VERCEL_URL" in os.environ:
    vercel_url = f"https://{os.environ['VERCEL_URL']}"
    allowed_origins.append(vercel_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
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
        logger.info(f"Processing video {video_id} for job {job_id}")
        
        # Simulate processing delay
        await asyncio.sleep(2)
        
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
        
        logger.info(f"Video processing completed for job {job_id}")
        
    except Exception as e:
        logger.error(f"Video processing failed for job {job_id}: {str(e)}")

@api_router.get("/learning/daily-tip")
async def get_daily_tip(
    session_token: Optional[str] = Cookie(None),
    authorization: Optional[str] = Header(None)
):
    user = get_current_user(session_token, authorization)
    tip = await get_current_daily_tip()
    return tip

@api_router.get("/learning/ted-talks")
async def get_ted_talks(
    session_token: Optional[str] = Cookie(None),
    authorization: Optional[str] = Header(None)
):
    get_current_user(session_token, authorization)
    # Mock TED talks data
    ted_talks = [
        {
            "id": "1",
            "title": "How to speak so that people want to listen",
            "speaker": "Julian Treasure",
            "duration": "9:59",
            "views": "25M",
            "link": "https://www.ted.com/talks/julian_treasure_how_to_speak_so_that_people_want_to_listen"
        }
    ]
    return ted_talks

@api_router.get("/training/modules")
async def get_training_modules(
    session_token: Optional[str] = Cookie(None),
    authorization: Optional[str] = Header(None)
):
    get_current_user(session_token, authorization)
    # Return list of available training modules
    modules = [
        {"id": "strategic-pauses", "title": "Strategic Pauses", "duration": "3 min"},
        {"id": "lens-eye-contact", "title": "Lens Eye Contact", "duration": "4 min"}
    ]
    return modules

@api_router.get("/simulator/scenarios")
async def get_simulator_scenarios(
    session_token: Optional[str] = Cookie(None),
    authorization: Optional[str] = Header(None)
):
    get_current_user(session_token, authorization)
    # Get current scenarios based on rotation period
    scenarios = await get_current_simulator_scenarios()
    return scenarios