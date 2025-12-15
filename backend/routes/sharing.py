from fastapi import APIRouter, HTTPException, Cookie, Header
from typing import Optional
from datetime import datetime, timezone, timedelta
import uuid

from utils.auth import get_current_user

# Mock storage for report shares and reports
report_shares = {}
shared_reports = {}

def create_sharing_router(supabase):
    router = APIRouter(tags=["sharing"])

    @router.post("/reports/{report_id}/share")
    async def create_report_share_link(
        report_id: str,
        session_token: Optional[str] = Cookie(None),
        authorization: Optional[str] = Header(None),
    ):
        user = get_current_user(session_token, authorization)

        # Check if report exists (mock implementation)
        # In a real app, you would check if the report belongs to the user
        report_exists = True  # Simplified for demo
        
        if not report_exists:
            raise HTTPException(status_code=404, detail="Report not found")

        share_id = f"share_{uuid.uuid4().hex}"
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(days=7)

        doc = {
            "id": share_id,
            "report_id": report_id,
            "owner_user_id": user["user_id"],
            "created_at": now.isoformat(),
            "expires_at": expires_at.isoformat(),
            "revoked": False,
        }

        # Save share link
        report_shares[share_id] = doc
            
        return {"share_id": share_id, "expires_at": expires_at.isoformat()}

    @router.get("/shared/reports/{share_id}")
    async def get_shared_report(share_id: str):
        share = report_shares.get(share_id)
        
        if not share:
            raise HTTPException(status_code=404, detail="Share link not found")
                
        if share.get("revoked"):
            raise HTTPException(status_code=404, detail="Share link not found")

        expires_at = share.get("expires_at")
        if expires_at:
            exp = datetime.fromisoformat(expires_at)
            if exp.tzinfo is None:
                exp = exp.replace(tzinfo=timezone.utc)
            if exp < datetime.now(timezone.utc):
                raise HTTPException(status_code=410, detail="Share link expired")

        # Mock report data
        report = {
            "id": share["report_id"],
            "content": {
                "executive_presence_score": 85,
                "feedback": "Great presentation skills demonstrated",
                "recommendations": ["Improve eye contact", "Work on posture"]
            },
            "created_at": datetime.now(timezone.utc).isoformat()
        }

        # Hide internal identifiers
        report.pop("user_id", None)
        return {"share": share, "report": report}

    return router