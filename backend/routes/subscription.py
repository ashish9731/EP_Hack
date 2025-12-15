"""
Subscription management routes
"""
from fastapi import APIRouter, HTTPException, Header, Cookie
from typing import Optional
from datetime import datetime, timezone, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel

router = APIRouter()

# Whitelisted emails with permanent Pro access
WHITELISTED_EMAILS = [
    "ashish9731@gmail.com",
    "ankur@c2x.co.in",
    "Likitha@c2x.co.in"
]

SUBSCRIPTION_TIERS = {
    "free": {
        "name": "Free Trial",
        "duration_days": 2,
        "video_limit": 1,
        "simulator_limit": 2,
        "learning_bytes_limit": 2,
        "can_download": False,
        "features": ["basic_report", "preview_only"]
    },
    "basic": {
        "name": "Basic",
        "video_limit": 7,
        "simulator_limit": 10,
        "learning_bytes_limit": -1,  # unlimited
        "can_download": True,
        "features": ["basic_ep_score", "report_download", "basic_analytics"]
    },
    "pro": {
        "name": "Pro",
        "video_limit": -1,  # unlimited
        "simulator_limit": -1,
        "learning_bytes_limit": -1,
        "can_download": True,
        "features": ["advanced_ep_score", "report_download", "report_sharing", "advanced_analytics", "priority_support"]
    },
    "enterprise": {
        "name": "Enterprise",
        "video_limit": -1,
        "simulator_limit": -1,
        "learning_bytes_limit": -1,
        "can_download": True,
        "features": ["custom_branding", "team_management", "sla"]
    }
}

class UpgradeRequest(BaseModel):
    tier: str
    billing_cycle: str  # monthly or yearly


async def check_subscription_status(db: AsyncIOMotorDatabase, user_id: str, email: str) -> dict:
    """Check if user has active subscription and their limits"""
    
    # Check if whitelisted
    if email.lower() in [e.lower() for e in WHITELISTED_EMAILS]:
        return {
            "tier": "pro",
            "status": "active",
            "is_whitelisted": True,
            "video_limit": -1,
            "videos_used": 0,
            "can_download": True,
            "features": SUBSCRIPTION_TIERS["pro"]["features"]
        }
    
    # Get user subscription
    subscription = await db.subscriptions.find_one({"user_id": user_id}, {"_id": 0})
    
    if not subscription:
        # Create free trial subscription
        trial_end = datetime.now(timezone.utc) + timedelta(days=2)
        subscription = {
            "user_id": user_id,
            "email": email,
            "tier": "free",
            "status": "active",
            "started_at": datetime.now(timezone.utc),
            "expires_at": trial_end,
            "videos_used_this_month": 0,
            "device_fingerprints": [],
            "is_whitelisted": False
        }
        await db.subscriptions.insert_one(subscription)
        subscription.pop("_id", None)
    
    # Check if expired
    if subscription.get("expires_at") and subscription["expires_at"] < datetime.now(timezone.utc):
        subscription["status"] = "expired"
        await db.subscriptions.update_one(
            {"user_id": user_id},
            {"$set": {"status": "expired"}}
        )
    
    tier_info = SUBSCRIPTION_TIERS.get(subscription["tier"], SUBSCRIPTION_TIERS["free"])
    
    return {
        "tier": subscription["tier"],
        "status": subscription["status"],
        "is_whitelisted": subscription.get("is_whitelisted", False),
        "video_limit": tier_info["video_limit"],
        "videos_used": subscription.get("videos_used_this_month", 0),
        "can_download": tier_info["can_download"],
        "features": tier_info["features"],
        "expires_at": subscription.get("expires_at")
    }


async def check_device_fingerprint(db: AsyncIOMotorDatabase, fingerprint: str, email: str) -> bool:
    """Check if device has already used free trial"""
    
    # Check if device exists
    device = await db.device_fingerprints.find_one({"fingerprint": fingerprint}, {"_id": 0})
    
    if device and device.get("free_trial_used"):
        # Device has used free trial
        return False
    
    # Check if this email has used free trial on another device
    existing_sub = await db.subscriptions.find_one({"email": email, "tier": {"$ne": "free"}}, {"_id": 0})
    if existing_sub:
        # Email has paid subscription, allow
        return True
    
    # Check if email used trial on different device
    trial_sub = await db.subscriptions.find_one({"email": email, "tier": "free"}, {"_id": 0})
    if trial_sub and fingerprint not in trial_sub.get("device_fingerprints", []):
        # Email already used trial on different device
        return False
    
    return True


def get_subscription_routes(db: AsyncIOMotorDatabase):
    from utils.auth import get_current_user
    
    @router.get("/subscription/status")
    async def get_subscription_status(
        session_token: Optional[str] = Cookie(None),
        authorization: Optional[str] = Header(None),
        device_fingerprint: Optional[str] = Header(None, alias="X-Device-Fingerprint")
    ):
        user = await get_current_user(db, session_token, authorization)
        subscription = await check_subscription_status(db, user["user_id"], user["email"])
        
        # Add device fingerprint if provided
        if device_fingerprint:
            await db.subscriptions.update_one(
                {"user_id": user["user_id"]},
                {"$addToSet": {"device_fingerprints": device_fingerprint}}
            )
            
            # Update device record
            await db.device_fingerprints.update_one(
                {"fingerprint": device_fingerprint},
                {
                    "$set": {
                        "user_id": user["user_id"],
                        "email": user["email"],
                        "last_seen": datetime.now(timezone.utc)
                    },
                    "$setOnInsert": {
                        "first_seen": datetime.now(timezone.utc),
                        "free_trial_used": subscription["tier"] == "free"
                    }
                },
                upsert=True
            )
        
        return subscription
    
    @router.post("/subscription/upgrade")
    async def upgrade_subscription(
        request: UpgradeRequest,
        session_token: Optional[str] = Cookie(None),
        authorization: Optional[str] = Header(None),
        device_fingerprint: Optional[str] = Header(None, alias="X-Device-Fingerprint")
    ):
        user = await get_current_user(db, session_token, authorization)
        
        # Check if device is allowed to use free trial
        if request.tier == "free" and device_fingerprint:
            allowed = await check_device_fingerprint(db, device_fingerprint, user["email"])
            if not allowed:
                raise HTTPException(
                    status_code=403,
                    detail="Free trial already used on this device or email. Please upgrade to continue."
                )
        
        # For free tier, no payment needed
        if request.tier == "free":
            expires_at = datetime.now(timezone.utc) + timedelta(days=2)
            
            await db.subscriptions.update_one(
                {"user_id": user["user_id"]},
                {
                    "$set": {
                        "tier": request.tier,
                        "status": "active",
                        "expires_at": expires_at,
                        "updated_at": datetime.now(timezone.utc)
                    }
                },
                upsert=True
            )
            
            if device_fingerprint:
                await db.device_fingerprints.update_one(
                    {"fingerprint": device_fingerprint},
                    {"$set": {"free_trial_used": True}}
                )
            
            return {
                "success": True,
                "tier": request.tier,
                "message": "Free trial activated"
            }
        
        # For paid tiers, create Dodo payment session
        from services.dodo_payment import create_payment_session
        
        payment_result = await create_payment_session(
            tier=request.tier,
            billing_cycle=request.billing_cycle,
            user_email=user["email"],
            user_id=user["user_id"]
        )
        
        if "error" in payment_result:
            raise HTTPException(status_code=500, detail=payment_result["error"])
        
        # Store pending subscription upgrade
        await db.pending_subscriptions.update_one(
            {"user_id": user["user_id"]},
            {
                "$set": {
                    "tier": request.tier,
                    "billing_cycle": request.billing_cycle,
                    "payment_session_id": payment_result.get("session_id"),
                    "created_at": datetime.now(timezone.utc)
                }
            },
            upsert=True
        )
        
        return {
            "success": True,
            "checkout_url": payment_result["checkout_url"],
            "message": "Redirecting to payment..."
        }
    
    @router.post("/subscription/check-video-limit")
    async def check_video_limit(
        session_token: Optional[str] = Cookie(None),
        authorization: Optional[str] = Header(None)
    ):
        user = await get_current_user(db, session_token, authorization)
        subscription = await check_subscription_status(db, user["user_id"], user["email"])
        
        if subscription["status"] == "expired":
            raise HTTPException(
                status_code=403,
                detail="Your subscription has expired. Please upgrade to continue."
            )
        
        video_limit = subscription["video_limit"]
        videos_used = subscription["videos_used"]
        
        if video_limit != -1 and videos_used >= video_limit:
            raise HTTPException(
                status_code=403,
                detail=f"You've reached your monthly limit of {video_limit} videos. Upgrade to continue."
            )
        
        return {"allowed": True, "remaining": video_limit - videos_used if video_limit != -1 else -1}
    
    @router.post("/subscription/increment-usage")
    async def increment_video_usage(
        session_token: Optional[str] = Cookie(None),
        authorization: Optional[str] = Header(None)
    ):
        user = await get_current_user(db, session_token, authorization)
        
        await db.subscriptions.update_one(
            {"user_id": user["user_id"]},
            {"$inc": {"videos_used_this_month": 1}}
        )
        
        return {"success": True}
    
    return router
