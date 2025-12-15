from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File, Depends, Response, Cookie, Header
from fastapi.responses import StreamingResponse, FileResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
# Removed MongoDB client import
import os
import logging
from pathlib import Path
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
from utils.supabase_auth import create_session_token, get_current_user, hash_password, verify_password
from utils.gridfs_helper import save_video_to_gridfs, get_video_from_gridfs
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

# Removed MongoDB URL initialization
# Removed MongoDB client initialization
# Removed MongoDB database initialization

app = FastAPI()
api_router = APIRouter(prefix="/api")

video_processor = None

def get_video_processor():
    global video_processor
    if video_processor is None:
        video_processor = VideoProcessorService(db)
    return video_processor

@api_router.post("/auth/signup")
async def signup(request: SignupRequest, response: Response):
    existing = await db.users.find_one({"email": request.email}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_id = f"user_{uuid.uuid4().hex[:12]}"
    hashed_pw = await hash_password(request.password)
    
    user_doc = {
        "user_id": user_id,
        "email": request.email,
        "name": request.name,
        "picture": None,
        "password_hash": hashed_pw,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.users.insert_one(user_doc)
    
    session_token = await create_session_token(db, user_id)
    
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=True,
        samesite="none",
        path="/",
        max_age=7 * 24 * 60 * 60
    )
    
    user = await db.users.find_one({"user_id": user_id}, {"_id": 0, "password_hash": 0})
    
    return {"user": user, "session_token": session_token}

@api_router.post("/auth/login")
async def login(request: LoginRequest, response: Response):
    user_doc = await db.users.find_one({"email": request.email}, {"_id": 0})
    
    if not user_doc or not await verify_password(request.password, user_doc.get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    session_token = await create_session_token(db, user_doc["user_id"])
    
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
        
        existing_user = await db.users.find_one({"email": data["email"]}, {"_id": 0})
        
        if existing_user:
            user_id = existing_user["user_id"]
            await db.users.update_one(
                {"user_id": user_id},
                {"$set": {
                    "name": data.get("name", existing_user["name"]),
                    "picture": data.get("picture", existing_user.get("picture"))
                }}
            )
        else:
            user_id = f"user_{uuid.uuid4().hex[:12]}"
            user_doc = {
                "user_id": user_id,
                "email": data["email"],
                "name": data.get("name", ""),
                "picture": data.get("picture"),
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            await db.users.insert_one(user_doc)
        
        session_token = data.get("session_token") or await create_session_token(db, user_id)
        
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        await db.user_sessions.update_one(
            {"session_token": session_token},
            {"$set": {
                "user_id": user_id,
                "session_token": session_token,
                "expires_at": expires_at.isoformat(),
                "created_at": datetime.now(timezone.utc).isoformat()
            }},
            upsert=True
        )
        
        user = await db.users.find_one({"user_id": user_id}, {"_id": 0, "password_hash": 0})
        
        return {"user": user, "session_token": session_token}

@api_router.get("/auth/me")
async def get_me(session_token: Optional[str] = Cookie(None), authorization: Optional[str] = Header(None)):
    user = await get_current_user(db, session_token, authorization)
    return user

@api_router.post("/auth/logout")
async def logout(response: Response, session_token: Optional[str] = Cookie(None)):
    if session_token:
        await db.user_sessions.delete_one({"session_token": session_token})
        response.delete_cookie("session_token", path="/")
    return {"message": "Logged out"}

@api_router.post("/videos/upload")
async def upload_video(
    file: UploadFile = File(...),
    session_token: Optional[str] = Cookie(None),
    authorization: Optional[str] = Header(None)
):
    user = await get_current_user(db, session_token, authorization)
    
    if file.size and file.size > 200 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Video size exceeds 200MB limit")
    
    video_id = await save_video_to_gridfs(db, file)
    
    metadata_doc = {
        "video_id": video_id,
        "user_id": user["user_id"],
        "filename": file.filename,
        "file_size": file.size or 0,
        "format": file.content_type,
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
        "retention_policy": "30_days",
        "scheduled_deletion": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
    }
    
    # Check for user's default retention setting
    user_settings = await db.user_settings.find_one({"user_id": user["user_id"]}, {"_id": 0})
    if user_settings and user_settings.get("default_retention"):
        from services.video_retention import RETENTION_PERIODS
        policy = user_settings["default_retention"]
        days = RETENTION_PERIODS.get(policy)
        metadata_doc["retention_policy"] = policy
        metadata_doc["scheduled_deletion"] = (datetime.now(timezone.utc) + timedelta(days=days)).isoformat() if days else None
    
    await db.video_metadata.insert_one(metadata_doc)
    
    return {"video_id": video_id, "message": "Video uploaded successfully"}

@api_router.post("/videos/{video_id}/process")
async def process_video(
    video_id: str,
    session_token: Optional[str] = Cookie(None),
    authorization: Optional[str] = Header(None)
):
    user = await get_current_user(db, session_token, authorization)
    
    metadata = await db.video_metadata.find_one({"video_id": video_id, "user_id": user["user_id"]}, {"_id": 0})
    if not metadata:
        raise HTTPException(status_code=404, detail="Video not found")
    
    job_id = f"job_{uuid.uuid4().hex}"
    
    job_doc = {
        "job_id": job_id,
        "user_id": user["user_id"],
        "video_id": video_id,
        "status": "pending",
        "progress": 0.0,
        "current_step": "Initializing...",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.video_jobs.insert_one(job_doc)
    
    processor = get_video_processor()
    asyncio.create_task(processor.process_video(job_id, video_id, user["user_id"]))
    
    return {"job_id": job_id, "message": "Processing started"}

@api_router.get("/jobs/{job_id}/status")
async def get_job_status(
    job_id: str,
    session_token: Optional[str] = Cookie(None),
    authorization: Optional[str] = Header(None)
):
    user = await get_current_user(db, session_token, authorization)
    
    job = await db.video_jobs.find_one({"job_id": job_id, "user_id": user["user_id"]}, {"_id": 0})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job

@api_router.get("/reports/{report_id}")
async def get_report(
    report_id: str,
    session_token: Optional[str] = Cookie(None),
    authorization: Optional[str] = Header(None)
):
    user = await get_current_user(db, session_token, authorization)
    
    report = await db.ep_reports.find_one({"report_id": report_id, "user_id": user["user_id"]}, {"_id": 0})
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return report

@api_router.get("/reports")
async def list_reports(
    session_token: Optional[str] = Cookie(None),
    authorization: Optional[str] = Header(None)
):
    user = await get_current_user(db, session_token, authorization)
    
    reports = await db.ep_reports.find({"user_id": user["user_id"]}, {"_id": 0}).sort("created_at", -1).to_list(50)
    
    return {"reports": reports}

coaching_router = create_coaching_router(db)
sharing_router = create_sharing_router(db)
retention_router, retention_service = create_retention_router(db)
api_router.include_router(coaching_router)
api_router.include_router(sharing_router)
api_router.include_router(retention_router)

profile_router = create_profile_router(db)
api_router.include_router(profile_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=[
        "http://localhost:3000",
        "https://exec-presence.preview.emergentagent.com"
    ],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

@api_router.get("/learning/daily-tip")
async def get_daily_tip(
    session_token: Optional[str] = Cookie(None),
    authorization: Optional[str] = Header(None)
):
    user = await get_current_user(db, session_token, authorization)
    
    # Get timed daily tip
    tip_data = get_current_daily_tip()
    
    return {
        "tip": tip_data["tip"],
        "category": tip_data["category"],
        "date": datetime.now(timezone.utc).isoformat(),
        "rotation_info": tip_data["rotation_info"],
        "tip_number": tip_data["tip_number"],
        "total_tips": tip_data["total_tips"]
    }

# Public-facing learning/training endpoints are defined below; include router at the end of file.


@api_router.get("/learning/ted-talks")
async def get_ted_talks(
    session_token: Optional[str] = Cookie(None),
    authorization: Optional[str] = Header(None)
):
    await get_current_user(db, session_token, authorization)
    
    # Only include videos that are confirmed to work with embedding
    talks = [
        {
            "id": 1,
            "title": "Your body language may shape who you are",
            "speaker": "Amy Cuddy",
            "duration": "21 min",
            "relevance": "Presence, Body Language, Confidence",
            "url": "https://www.ted.com/talks/amy_cuddy_your_body_language_may_shape_who_you_are",
            "embed_url": "https://embed.ted.com/talks/amy_cuddy_your_body_language_may_shape_who_you_are",
            "description": "Learn how power posing and body language influence confidence and presence"
        },
        {
            "id": 2,
            "title": "How great leaders inspire action",
            "speaker": "Simon Sinek",
            "duration": "18 min",
            "relevance": "Vision Articulation, Leadership, Communication",
            "url": "https://www.ted.com/talks/simon_sinek_how_great_leaders_inspire_action",
            "embed_url": "https://embed.ted.com/talks/simon_sinek_how_great_leaders_inspire_action",
            "description": "Discover the power of starting with 'why' in leadership communication"
        },
        {
            "id": 3,
            "title": "How to speak so that people want to listen",
            "speaker": "Julian Treasure",
            "duration": "10 min",
            "relevance": "Communication, Vocal Presence, Clarity",
            "url": "https://www.ted.com/talks/julian_treasure_how_to_speak_so_that_people_want_to_listen",
            "embed_url": "https://embed.ted.com/talks/julian_treasure_how_to_speak_so_that_people_want_to_listen",
            "description": "Master vocal techniques for more effective speaking"
        }
    ]
    
    return {"talks": talks}

@api_router.get("/training/modules")
async def get_training_modules(
    session_token: Optional[str] = Cookie(None),
    authorization: Optional[str] = Header(None)
):
    await get_current_user(db, session_token, authorization)
    
    # Get timed training modules (rotates weekly)
    training_data = get_current_training_modules()
    
    return {
        "modules": training_data["modules"],
        "rotation_info": training_data["rotation_info"],
        "week_theme": training_data["week_theme"],
        "week_number": training_data["week_number"]
    }

@api_router.get("/simulator/scenarios")
async def get_simulator_scenarios(
    session_token: Optional[str] = Cookie(None),
    authorization: Optional[str] = Header(None)
):
    await get_current_user(db, session_token, authorization)
    
    # Get timed simulator scenarios (rotates every 3 days)
    scenario_data = get_current_simulator_scenarios()
    
    return {
        "scenarios": scenario_data["scenarios"],
        "rotation_info": scenario_data["rotation_info"],
        "pool_name": scenario_data["pool_name"]
    }

@api_router.get("/training/modules/{module_id}")
async def get_module_content(
    module_id: str,
    session_token: Optional[str] = Cookie(None),
    authorization: Optional[str] = Header(None)
):
    user = await get_current_user(db, session_token, authorization)
    profile = await db.user_profiles.find_one({"user_id": user["user_id"]}, {"_id": 0})
    
    import openai
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    role_context = f"{profile.get('role', 'Executive')} at {profile.get('seniority_level', 'Senior')} level" if profile else "executive"
    
    module_prompts = {
        "strategic-pauses": "strategic pause techniques for executives",
        "lens-eye-contact": "camera eye contact and lens presence",
        "decision-framing": "executive decision communication framework",
        "vocal-variety": "vocal modulation and variety techniques",
        "storytelling-structure": "leadership storytelling structure",
        "commanding-openings": "commanding opening statements for executives"
    }
    
    topic = module_prompts.get(module_id, "executive presence")
    
    prompt = f"""Create a micro-training module on {topic} for a {role_context}.

Structure (keep concise):
1. **Key Concept** (2-3 sentences)
2. **Why It Matters** (2 sentences)
3. **3 Practical Techniques** (each 1-2 sentences)
4. **Practice Prompt** (specific scenario to practice)

Keep it actionable and professional. Total: ~200 words."""
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=400
    )
    
    content = response.choices[0].message.content
    
    return {
        "module_id": module_id,
        "content": content,
        "generated_at": datetime.now(timezone.utc).isoformat()
    }


# Ensure routes registered after all endpoints are declared
app.include_router(api_router)

# Include subscription routes
subscription_router = get_subscription_routes(db)
app.include_router(subscription_router, prefix="/api", tags=["subscription"])
