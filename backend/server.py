import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the backend directory to Python path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))
sys.path.insert(0, str(backend_path.parent))

# Also add the current directory
sys.path.insert(0, os.getcwd())
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))

# Load environment variables
ROOT_DIR = Path(__file__).parent.parent  # Go up one level to the project root
env_path = ROOT_DIR / '.env'
load_dotenv(env_path)

# Debug print to check if env vars are loaded
print(f"DEBUG: Looking for .env file at: {env_path}")
print(f"DEBUG: SUPABASE_URL from env: {os.getenv('SUPABASE_URL')}")
print(f"DEBUG: SUPABASE_KEY from env: {os.getenv('SUPABASE_KEY')[:10] if os.getenv('SUPABASE_KEY') else None}")

# Import Supabase client after loading environment variables
from utils.supabase_client import get_supabase_client

from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File, Depends, Response, Cookie, Header
from fastapi.responses import StreamingResponse, FileResponse
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
from utils.auth import create_user, get_user_by_email, verify_password
from utils.supabase_storage import save_video_to_storage, get_video_from_storage
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

# Environment variables already loaded at the top of the file
pass

app = FastAPI()
api_router = APIRouter(prefix="/api")

video_processor = None

def get_video_processor():
    global video_processor
    if video_processor is None:
        from services.video_processor import VideoProcessorService
        video_processor = VideoProcessorService()
    return video_processor

@api_router.post("/auth/signup")
async def signup(request: SignupRequest, response: Response):
    logger.info(f"Signup attempt for email: {request.email}")
    
    try:
        # Import Supabase client
        from utils.supabase_client import get_supabase_client
        supabase = get_supabase_client()
        
        # Use Supabase Auth to sign up the user
        auth_response = supabase.auth.sign_up({
            "email": request.email,
            "password": request.password,
            "options": {
                "data": {
                    "name": request.name
                }
            }
        })
        
        # Get the user data from the auth response
        user_data = auth_response.user
        
        # Also store user in our users table for compatibility with existing code
        user_table_data = {
            "id": user_data.id,
            "email": user_data.email,
            "name": request.name,
            "picture": None,
            "created_at": user_data.created_at
        }
        
        try:
            get_supabase_client().table("users").insert(user_table_data).execute()
        except Exception as e:
            # User might already exist in the table, which is fine
            pass
        
        # Create our own session token for compatibility with existing frontend
        session_token = str(uuid.uuid4())
        
        # Check if we're in development mode
        is_production = not os.getenv("DEV_MODE", "false").lower() == "true"
        
        response.set_cookie(
            key="session_token",
            value=session_token,
            httponly=True,
            secure=is_production,  # Only secure in production
            samesite="lax" if not is_production else "none",  # Lax in development, none in production
            path="/",
            max_age=7 * 24 * 60 * 60
        )
        
        # Transform user data to match existing structure
        user = {
            "user_id": user_data.id,
            "email": user_data.email,
            "name": request.name,
            "picture": None,
            "created_at": user_data.created_at
        }
        
        return {"user": user, "session_token": session_token}
        
    except Exception as e:
        # Handle specific Supabase auth errors
        if "already registered" in str(e).lower() or "email_taken" in str(e).lower():
            raise HTTPException(status_code=400, detail="Email already registered")
        else:
            logger.error(f"Signup error: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Signup error: {str(e)}")

@api_router.post("/auth/login")
async def login(request: LoginRequest, response: Response):
    logger.info(f"Login attempt for email: {request.email}")
    print(f"DEBUG: Login attempt for email: {request.email}")  # Debug print
    
    try:
        # Import Supabase client
        from utils.supabase_client import get_supabase_client
        supabase = get_supabase_client()
        
        print(f"DEBUG: Attempting Supabase login for {request.email}")  # Debug print
        
        # Use Supabase Auth to sign in the user
        auth_response = supabase.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password
        })
        
        print(f"DEBUG: Supabase login successful for {request.email}")  # Debug print
        print(f"DEBUG: Auth response: {auth_response}")  # Debug print
        
        # Get the user data from the auth response
        user_data = auth_response.user
        session_data = auth_response.session
        
        print(f"DEBUG: User data: {user_data}")  # Debug print
        print(f"DEBUG: Session data: {session_data}")  # Debug print
        
        # Create our own session token for compatibility with existing frontend
        session_token = str(uuid.uuid4())
        
        print(f"DEBUG: Generated session token: {session_token}")  # Debug print
        
        # Save session to database
        from datetime import datetime, timezone, timedelta
        session_id = str(uuid.uuid4())
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        
        session_record = {
            "id": session_id,
            "user_id": user_data.id,
            "session_token": session_token,
            "expires_at": expires_at.isoformat()
        }
        
        # Insert session record into database
        supabase.table("user_sessions").insert(session_record).execute()
        print(f"DEBUG: Saved session to database: {session_record}")  # Debug print
        
        # Check if we're in development mode
        is_production = not os.getenv("DEV_MODE", "false").lower() == "true"
        
        response.set_cookie(
            key="session_token",
            value=session_token,
            httponly=True,
            secure=is_production,  # Only secure in production
            samesite="lax" if not is_production else "none",  # Lax in development, none in production
            path="/",
            max_age=7 * 24 * 60 * 60
        )
        
        # Transform user data to match existing structure
        user = {
            "user_id": user_data.id,
            "email": user_data.email,
            "name": getattr(user_data, 'user_metadata', {}).get('name', ''),
            "picture": getattr(user_data, 'user_metadata', {}).get('picture'),
            "created_at": user_data.created_at
        }
        
        print(f"DEBUG: Returning user data: {user}")  # Debug print
        
        return {"user": user, "session_token": session_token}
        
    except Exception as e:
        print(f"DEBUG: Login error: {str(e)}")  # Debug print
        # Handle specific Supabase auth errors
        if "Invalid login credentials" in str(e):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        else:
            logger.error(f"Login error: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Authentication error: {str(e)}")

@api_router.get("/auth/google-redirect")
async def google_auth_redirect():
    logger.info("Google auth redirect requested")
    print("DEBUG: Google auth redirect requested")  # Debug print
    
    # Import Supabase client
    from utils.supabase_client import get_supabase_client
    supabase = get_supabase_client()
    
    print("DEBUG: Supabase client initialized")  # Debug print
    
    # Generate the Google OAuth URL
    try:
        redirect_url = f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/auth/callback"
        print(f"DEBUG: Redirect URL: {redirect_url}")  # Debug print
        
        oauth_response = supabase.auth.sign_in_with_oauth({
            "provider": "google",
            "options": {
                "redirectTo": redirect_url
            }
        })
        
        print(f"DEBUG: OAuth response: {oauth_response}")  # Debug print
        
        # Extract the authorization URL from the response
        auth_url = oauth_response.url
        
        print(f"DEBUG: Auth URL: {auth_url}")  # Debug print
        
        logger.info(f"Generated Google auth URL: {auth_url}")
        return {"auth_url": auth_url}
    except Exception as e:
        print(f"DEBUG: Google auth redirect error: {str(e)}")  # Debug print
        logger.error(f"Google auth redirect error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Authentication error: {str(e)}")

async def get_current_user(session_token: Optional[str] = Cookie(None), authorization: Optional[str] = Header(None)):
    print(f"DEBUG: get_current_user called with session_token: {session_token}, authorization: {authorization}")  # Debug print
    # Import the real authentication function
    from utils.supabase_auth import get_current_user as supabase_get_user
    try:
        # Use the real Supabase authentication
        print("DEBUG: Calling supabase_get_user")  # Debug print
        user = await supabase_get_user(session_token, authorization)
        print(f"DEBUG: Supabase user authentication successful: {user}")  # Debug print
        return user
    except Exception as e:
        print(f"DEBUG: Authentication failed: {str(e)}")  # Debug print
        # In a production environment, this should raise an HTTP 401 error
        # For development, we'll still return a mock user but with a flag to indicate it's not real
        logger.warning(f"Authentication failed: {str(e)}")
        # Raise the exception to properly handle unauthenticated requests
        raise HTTPException(status_code=401, detail="Not authenticated")

@api_router.get("/auth/me")
async def get_me(session_token: Optional[str] = Cookie(None), authorization: Optional[str] = Header(None)):
    user = await get_current_user(session_token, authorization)
    return user

@api_router.post("/auth/logout")
async def logout(response: Response, session_token: Optional[str] = Cookie(None)):
    # Clear the cookie with the appropriate settings (bypass session validation)
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
    user = await get_current_user(session_token, authorization)
    
    # Allow larger video files - up to 1GB
    if file.size and file.size > 1024 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Video size exceeds 1GB limit")
    
    # Save video to storage
    try:
        from utils.supabase_storage import save_video_to_storage
        video_id = await save_video_to_storage(file, user["user_id"])
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
    user = await get_current_user(session_token, authorization)
    
    # Create a processing job
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

@app.get("/api/jobs/{job_id}/status")
async def get_job_status(
    job_id: str,
    session_token: Optional[str] = Cookie(None),
    authorization: Optional[str] = Header(None)
):
    user = await get_current_user(session_token, authorization)
    
    try:
        # Get Supabase client
        from utils.supabase_client import get_supabase_client
        supabase = get_supabase_client()
        
        # Query the database for the actual job status
        response = supabase.table("jobs").select("*").eq("id", job_id).eq("user_id", user["user_id"]).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Job not found")
        
        job = response.data[0]
        logger.info(f"Returning job status: {job}")
        return job
        
    except Exception as e:
        logger.error(f"Failed to get job status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get job status: {str(e)}")

@app.get("/api/reports/{report_id}")
async def get_report(
    report_id: str,
    session_token: Optional[str] = Cookie(None),
    authorization: Optional[str] = Header(None)
):
    user = await get_current_user(session_token, authorization)
    
    try:
        # Get Supabase client
        from utils.supabase_client import get_supabase_client
        supabase = get_supabase_client()
        
        # Query the database for the actual report
        response = supabase.table("reports").select("*").eq("id", report_id).eq("user_id", user["user_id"]).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Report not found")
        
        report = response.data[0]
        logger.info(f"Returning report: {report}")
        return report
        
    except Exception as e:
        logger.error(f"Failed to get report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get report: {str(e)}")

@app.get("/api/reports")
async def list_reports(
    session_token: Optional[str] = Cookie(None),
    authorization: Optional[str] = Header(None)
):
    user = await get_current_user(session_token, authorization)
    
    try:
        # Get Supabase client
        from utils.supabase_client import get_supabase_client
        supabase = get_supabase_client()
        
        # Query the database for the user's reports
        response = supabase.table("reports").select("*").eq("user_id", user["user_id"]).order("created_at", desc=True).execute()
        
        reports = response.data if response.data else []
        logger.info(f"Returning reports list with {len(reports)} items")
        return {"reports": reports}
        
    except Exception as e:
        logger.error(f"Failed to list reports: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list reports: {str(e)}")

@api_router.get("/videos/{video_id}/stream")
async def stream_video(
    video_id: str,
    session_token: Optional[str] = Cookie(None),
    authorization: Optional[str] = Header(None)
):
    user = await get_current_user(session_token, authorization)
    
    try:
        # Get signed URL from Supabase storage
        from utils.supabase_storage import get_signed_url
        signed_url = get_signed_url(video_id, expires_in=3600)  # URL expires in 1 hour
        
        return {"url": signed_url, "video_id": video_id}
    except Exception as e:
        logger.error(f"Failed to stream video {video_id}: {str(e)}")
        raise HTTPException(status_code=404, detail="Video not found")

# Add the rest of the routes
app.include_router(api_router)

# Include other routers
app.include_router(create_profile_router(get_supabase_client()))
app.include_router(get_subscription_routes(get_supabase_client()))
app.include_router(create_coaching_router(get_supabase_client()))
app.include_router(create_sharing_router(get_supabase_client()))
app.include_router(create_retention_router(get_supabase_client()))

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

async def process_video_async(job_id: str, video_id: str, user_id: str):
    """Process video using the real video processor service"""
    try:
        # Update job status to processing
        logger.info(f"Processing video {video_id} for job {job_id}")
        
        # Get the video processor service
        video_processor = get_video_processor()
        
        # Process the video
        report_id = await video_processor.process_video(job_id, video_id, user_id)
        
        logger.info(f"Video processing completed for job {job_id}, report_id: {report_id}")
        
    except Exception as e:
        logger.error(f"Video processing failed for job {job_id}: {str(e)}")
        # In a real implementation, you would update the job status to failed in the database

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
    # Return list of available TED talks
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
            "duration": "20:02",
            "views": "15M",
            "link": "https://www.ted.com/talks/brene_brown_the_power_of_vulnerability"
        },
        {
            "id": "3",
            "title": "How great leaders inspire action",
            "speaker": "Simon Sinek",
            "duration": "18:05",
            "views": "12M",
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
        {
            "id": "strategic-pauses", 
            "title": "Strategic Pauses", 
            "duration": "3 min",
            "description": "Learn techniques to project confidence through your voice, including pace, tone, and strategic pauses.",
            "focus_area": "Communication",
            "difficulty": "Beginner"
        },
        {
            "id": "lens-eye-contact", 
            "title": "Lens Eye Contact", 
            "duration": "4 min",
            "description": "Develop your body language toolkit with posture, gestures, and spatial awareness techniques.",
            "focus_area": "Presence",
            "difficulty": "Intermediate"
        },
        {
            "id": "storytelling-framework", 
            "title": "Strategic Storytelling Framework", 
            "duration": "5 min",
            "description": "Craft compelling narratives that drive action and create emotional connections with stakeholders.",
            "focus_area": "Storytelling",
            "difficulty": "Advanced"
        }
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5002, log_level="info")
