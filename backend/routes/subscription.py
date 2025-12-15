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

class UpgradeRequest(BaseModel):
    tier: str
    billing_cycle: str  # monthly or yearly


async def check_subscription_status(supabase, user_id: str, email: str) -> dict:
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
    try:
        subscription_response = supabase.table("subscriptions").select("*").eq("user_id", user_id).execute()
        subscription = subscription_response.data[0] if subscription_response.data else None
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
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
        
        try:
            supabase.table("subscriptions").insert(subscription_data).execute()
            subscription = subscription_data
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create subscription: {str(e)}")
    
    # Check if expired
    if subscription.get("expires_at"):
        expires_at = subscription["expires_at"]
        if isinstance(expires_at, str):
            expires_at = datetime.fromisoformat(expires_at)
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
            
        if expires_at < datetime.now(timezone.utc):
            subscription["status"] = "expired"
            try:
                supabase.table("subscriptions").update({"status": "expired"}).eq("user_id", user_id).execute()
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to update subscription: {str(e)}")
    
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


async def check_device_fingerprint(supabase, fingerprint: str, email: str) -> bool:
    """Check if device has already used free trial"""
    
    # Check if device exists
    try:
        device_response = supabase.table("device_fingerprints").select("*").eq("fingerprint", fingerprint).execute()
        device = device_response.data[0] if device_response.data else None
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    if device and device.get("free_trial_used"):
        # Device has used free trial
        return False
    
    # Check if this email has used free trial on another device
    try:
        existing_sub_response = supabase.table("subscriptions").select("*").eq("email", email).neq("tier", "free").execute()
        if existing_sub_response.data:
            # Email has paid subscription, allow
            return True
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    # Check if email used trial on different device
    try:
        trial_sub_response = supabase.table("subscriptions").select("*").eq("email", email).eq("tier", "free").execute()
        if trial_sub_response.data:
            trial_sub = trial_sub_response.data[0]
            if fingerprint not in trial_sub.get("device_fingerprints", []):
                # Email already used trial on different device
                return False
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    return True


def get_subscription_routes(supabase):
    from utils.supabase_auth import get_current_user
    
    @router.get("/subscription/status")
    async def get_subscription_status(
        session_token: Optional[str] = Cookie(None),
        authorization: Optional[str] = Header(None),
        device_fingerprint: Optional[str] = Header(None, alias="X-Device-Fingerprint")
    ):
        user = await get_current_user(session_token, authorization)
        subscription = await check_subscription_status(supabase, user["user_id"], user["email"])
        
        # Add device fingerprint if provided
        if device_fingerprint:
            try:
                # Update subscription with device fingerprint
                subscription_response = supabase.table("subscriptions").select("device_fingerprints").eq("user_id", user["user_id"]).execute()
                if subscription_response.data:
                    current_fingerprints = subscription_response.data[0].get("device_fingerprints", [])
                    if device_fingerprint not in current_fingerprints:
                        current_fingerprints.append(device_fingerprint)
                        supabase.table("subscriptions").update({"device_fingerprints": current_fingerprints}).eq("user_id", user["user_id"]).execute()
                
                # Update device record
                device_data = {
                    "fingerprint": device_fingerprint,
                    "user_id": user["user_id"],
                    "email": user["email"],
                    "last_seen": datetime.now(timezone.utc).isoformat()
                }
                
                # Try to get existing device record
                device_response = supabase.table("device_fingerprints").select("*").eq("fingerprint", device_fingerprint).execute()
                if device_response.data:
                    # Update existing device record
                    supabase.table("device_fingerprints").update(device_data).eq("fingerprint", device_fingerprint).execute()
                else:
                    # Create new device record
                    device_data["first_seen"] = datetime.now(timezone.utc).isoformat()
                    device_data["free_trial_used"] = subscription["tier"] == "free"
                    supabase.table("device_fingerprints").insert(device_data).execute()
            except Exception as e:
                # Log error but don't fail the request
                print(f"Failed to update device fingerprint: {str(e)}")
        
        return subscription
    
    @router.post("/subscription/upgrade")
    async def upgrade_subscription(
        request: UpgradeRequest,
        session_token: Optional[str] = Cookie(None),
        authorization: Optional[str] = Header(None),
        device_fingerprint: Optional[str] = Header(None, alias="X-Device-Fingerprint")
    ):
        user = await get_current_user(session_token, authorization)
        
        # Check if device is allowed to use free trial
        if request.tier == "free" and device_fingerprint:
            allowed = await check_device_fingerprint(supabase, device_fingerprint, user["email"])
            if not allowed:
                raise HTTPException(
                    status_code=403,
                    detail="Free trial already used on this device or email. Please upgrade to continue."
                )
        
        # For free tier, no payment needed
        if request.tier == "free":
            expires_at = datetime.now(timezone.utc) + timedelta(days=2)
            
            try:
                # Update subscription
                update_data = {
                    "tier": "free",
                    "status": "active",
                    "expires_at": expires_at.isoformat(),
                    "billing_cycle": request.billing_cycle
                }
                supabase.table("subscriptions").update(update_data).eq("user_id", user["user_id"]).execute()
                
                # Mark device as having used free trial
                if device_fingerprint:
                    supabase.table("device_fingerprints").update({"free_trial_used": True}).eq("fingerprint", device_fingerprint).execute()
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to upgrade subscription: {str(e)}")
            
            return {"message": "Subscription upgraded to free tier", "tier": "free"}
        
        # For paid tiers, return payment info
        return {
            "message": "Redirect to payment gateway",
            "tier": request.tier,
            "billing_cycle": request.billing_cycle,
            "amount": "TBD"  # This would be calculated based on tier and cycle
        }
    
    return router