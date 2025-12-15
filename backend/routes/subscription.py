"""
Subscription management routes
"""
from fastapi import APIRouter, HTTPException, Header, Cookie
from typing import Optional
from datetime import datetime, timezone, timedelta
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

# Mock storage for subscriptions and devices
subscriptions = {}
device_fingerprints = {}

class UpgradeRequest(BaseModel):
    tier: str
    billing_cycle: str  # monthly or yearly

async def check_subscription_status(user_id: str, email: str) -> dict:
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
    subscription = subscriptions.get(user_id)
    
    if not subscription:
        # Create free trial subscription
        trial_end = datetime.now(timezone.utc) + timedelta(days=2)
        subscription_data = {
            "user_id": user_id,
            "email": email,
            "tier": "free",
            "status": "active",
            "started_at": datetime.now(timezone.utc).isoformat(),
            "expires_at": trial_end.isoformat(),
            "videos_used_this_month": 0,
            "device_fingerprints": [],
            "is_whitelisted": False
        }
        
        subscriptions[user_id] = subscription_data
        subscription = subscription_data
    
    # Check if expired
    if subscription.get("expires_at"):
        expires_at = subscription["expires_at"]
        if isinstance(expires_at, str):
            expires_at = datetime.fromisoformat(expires_at)
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
            
        if expires_at < datetime.now(timezone.utc):
            subscription["status"] = "expired"
            subscriptions[user_id] = subscription
    
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

async def check_device_fingerprint(fingerprint: str, email: str) -> bool:
    """Check if device has already used free trial"""
    
    # Check if device exists
    device = device_fingerprints.get(fingerprint)
    
    if device and device.get("free_trial_used"):
        # Device has used free trial
        return False
    
    # Check if this email has used free trial on another device
    # For simplicity, we'll just check if there's any paid subscription for this email
    for sub in subscriptions.values():
        if sub.get("email") == email and sub.get("tier") != "free":
            # Email has paid subscription, allow
            return True
    
    # Check if email used trial on different device
    for sub in subscriptions.values():
        if sub.get("email") == email and sub.get("tier") == "free":
            if fingerprint not in sub.get("device_fingerprints", []):
                # Email already used trial on different device
                return False
    
    return True

def get_subscription_routes(supabase):
    from utils.auth import get_current_user
    
    @router.get("/subscription/status")
    async def get_subscription_status(
        session_token: Optional[str] = Cookie(None),
        authorization: Optional[str] = Header(None),
        device_fingerprint: Optional[str] = Header(None, alias="X-Device-Fingerprint")
    ):
        user = get_current_user(session_token, authorization)
        subscription = await check_subscription_status(user["user_id"], user["email"])
        
        # Add device fingerprint if provided
        if device_fingerprint:
            # Update subscription with device fingerprint
            user_subscription = subscriptions.get(user["user_id"])
            if user_subscription:
                current_fingerprints = user_subscription.get("device_fingerprints", [])
                if device_fingerprint not in current_fingerprints:
                    current_fingerprints.append(device_fingerprint)
                    user_subscription["device_fingerprints"] = current_fingerprints
                    subscriptions[user["user_id"]] = user_subscription
            
            # Update device record
            device_data = {
                "fingerprint": device_fingerprint,
                "user_id": user["user_id"],
                "email": user["email"],
                "last_seen": datetime.now(timezone.utc).isoformat()
            }
            
            device_fingerprints[device_fingerprint] = device_data
        
        return subscription
    
    @router.post("/subscription/upgrade")
    async def upgrade_subscription(
        request: UpgradeRequest,
        session_token: Optional[str] = Cookie(None),
        authorization: Optional[str] = Header(None)
    ):
        user = get_current_user(session_token, authorization)
        
        if request.tier not in SUBSCRIPTION_TIERS:
            raise HTTPException(status_code=400, detail="Invalid tier")
        
        # Update subscription
        user_subscription = subscriptions.get(user["user_id"])
        if not user_subscription:
            # Create new subscription
            user_subscription = {
                "user_id": user["user_id"],
                "email": user["email"],
                "tier": request.tier,
                "status": "active",
                "started_at": datetime.now(timezone.utc).isoformat(),
                "videos_used_this_month": 0,
                "device_fingerprints": [],
                "is_whitelisted": False
            }
        else:
            user_subscription["tier"] = request.tier
            user_subscription["status"] = "active"
            user_subscription["started_at"] = datetime.now(timezone.utc).isoformat()
        
        subscriptions[user["user_id"]] = user_subscription
        
        return {"message": "Subscription upgraded successfully"}
    
    @router.post("/subscription/check-video-limit")
    async def check_video_limit(
        session_token: Optional[str] = Cookie(None),
        authorization: Optional[str] = Header(None)
    ):
        user = get_current_user(session_token, authorization)
        subscription = await check_subscription_status(user["user_id"], user["email"])
        
        if subscription["video_limit"] == -1:  # Unlimited
            return {"can_upload": True}
        
        if subscription["videos_used"] < subscription["video_limit"]:
            return {"can_upload": True}
        else:
            return {"can_upload": False, "message": "Video limit reached for your subscription tier"}
    
    @router.post("/subscription/increment-usage")
    async def increment_usage(
        session_token: Optional[str] = Cookie(None),
        authorization: Optional[str] = Header(None)
    ):
        user = get_current_user(session_token, authorization)
        user_subscription = subscriptions.get(user["user_id"])
        
        if user_subscription:
            user_subscription["videos_used_this_month"] = user_subscription.get("videos_used_this_month", 0) + 1
            subscriptions[user["user_id"]] = user_subscription
        
        return {"message": "Usage incremented"}
    
    return router