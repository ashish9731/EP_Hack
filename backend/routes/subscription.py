"""
Subscription management routes
"""
from fastapi import APIRouter, HTTPException, Header, Cookie
from typing import Optional
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel
import uuid

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

async def check_subscription_status(user_id: str, user_email: str, supabase_client):
    """Check user's subscription status"""
    # Check if user is whitelisted
    if user_email in WHITELISTED_EMAILS:
        return {
            "tier": "pro",
            "status": "active",
            "is_whitelisted": True,
            "limits": SUBSCRIPTION_TIERS["pro"]
        }
    
    try:
        # Query subscriptions table for user's active subscription
        response = supabase_client.table("subscriptions").select("*").eq("user_id", user_id).eq("status", "active").execute()
        
        if response.data:
            subscription = response.data[0]
            tier_info = SUBSCRIPTION_TIERS.get(subscription["plan_type"], SUBSCRIPTION_TIERS["free"])
            
            return {
                "tier": subscription["plan_type"],
                "status": subscription["status"],
                "start_date": subscription["start_date"],
                "end_date": subscription["end_date"],
                "auto_renew": subscription["auto_renew"],
                "is_whitelisted": False,
                "limits": tier_info
            }
        else:
            # No active subscription, return free tier
            return {
                "tier": "free",
                "status": "active",
                "is_whitelisted": False,
                "limits": SUBSCRIPTION_TIERS["free"]
            }
    except Exception as e:
        # On error, default to free tier
        return {
            "tier": "free",
            "status": "active",
            "is_whitelisted": False,
            "limits": SUBSCRIPTION_TIERS["free"]
        }

def get_subscription_routes(supabase):
    from utils.auth import get_current_user
    
    @router.get("/subscription/status")
    async def get_subscription_status(
        session_token: Optional[str] = Cookie(None),
        authorization: Optional[str] = Header(None),
        device_fingerprint: Optional[str] = Header(None, alias="X-Device-Fingerprint")
    ):
        user = await get_current_user(session_token, authorization)
        
        try:
            # Get Supabase client
            supabase_client = supabase()
            
            # Check subscription status
            subscription = await check_subscription_status(user["user_id"], user["email"], supabase_client)
            
            # Add device fingerprint if provided
            if device_fingerprint:
                try:
                    # Store device fingerprint in a devices table (you'll need to create this table)
                    device_data = {
                        "id": str(uuid.uuid4()),
                        "user_id": user["user_id"],
                        "fingerprint": device_fingerprint,
                        "last_seen": datetime.now(timezone.utc).isoformat()
                    }
                    
                    # Upsert device information
                    supabase_client.table("devices").upsert(device_data).execute()
                except Exception as e:
                    # Log error but don't fail the request
                    print(f"Failed to store device fingerprint: {str(e)}")
            
            return subscription
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get subscription status: {str(e)}")
    
    @router.post("/subscription/upgrade")
    async def upgrade_subscription(
        request: UpgradeRequest,
        session_token: Optional[str] = Cookie(None),
        authorization: Optional[str] = Header(None)
    ):
        user = await get_current_user(session_token, authorization)
        
        if request.tier not in SUBSCRIPTION_TIERS:
            raise HTTPException(status_code=400, detail="Invalid subscription tier")
        
        try:
            # Get Supabase client
            supabase_client = supabase()
            
            # Deactivate any existing active subscriptions
            supabase_client.table("subscriptions").update({"status": "cancelled"}).eq("user_id", user["user_id"]).eq("status", "active").execute()
            
            # Create new subscription
            now = datetime.now(timezone.utc)
            end_date = now + timedelta(days=30)  # 30 days for monthly plan
            
            if request.billing_cycle == "yearly":
                end_date = now + timedelta(days=365)
            
            subscription_data = {
                "id": f"sub_{uuid.uuid4().hex}",
                "user_id": user["user_id"],
                "plan_type": request.tier,
                "status": "active",
                "start_date": now.isoformat(),
                "end_date": end_date.isoformat(),
                "auto_renew": True
            }
            
            # Insert new subscription
            response = supabase_client.table("subscriptions").insert(subscription_data).execute()
            
            return response.data[0] if response.data else subscription_data
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to upgrade subscription: {str(e)}")
    
    return router