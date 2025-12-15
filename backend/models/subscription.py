"""
Subscription and device tracking models
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SubscriptionTier(BaseModel):
    tier: str  # free, basic, pro, enterprise
    monthly_price: float
    yearly_price: float
    video_limit: int  # -1 for unlimited
    simulator_limit: int  # -1 for unlimited
    learning_bytes_limit: int  # -1 for unlimited
    features: list[str]

class UserSubscription(BaseModel):
    user_id: str
    email: str
    tier: str  # free, basic, pro, enterprise
    status: str  # active, expired, cancelled
    started_at: datetime
    expires_at: Optional[datetime]
    videos_used_this_month: int = 0
    device_fingerprints: list[str] = []
    is_whitelisted: bool = False
    
class DeviceFingerprint(BaseModel):
    fingerprint: str
    user_id: Optional[str]
    email: Optional[str]
    first_seen: datetime
    last_seen: datetime
    free_trial_used: bool = False
