from fastapi import APIRouter, HTTPException, Cookie, Header
from typing import Optional
from datetime import datetime, timezone, timedelta
import uuid

from utils.supabase_auth import get_current_user


def create_sharing_router(supabase):
    router = APIRouter(tags=["sharing"])

    @router.post("/reports/{report_id}/share")
    async def create_report_share_link(
        report_id: str,
        session_token: Optional[str] = Cookie(None),
        authorization: Optional[str] = Header(None),
    ):
        user = await get_current_user(session_token, authorization)

        # Check if report exists and belongs to user
        try:
            report_response = supabase.table("ep_reports").select("*").eq("id", report_id).eq("user_id", user["user_id"]).execute()
            if not report_response.data:
                raise HTTPException(status_code=404, detail="Report not found")
            report = report_response.data[0]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

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

        try:
            supabase.table("report_shares").insert(doc).execute()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create share link: {str(e)}")
            
        return {"share_id": share_id, "expires_at": expires_at.isoformat()}

    @router.get("/shared/reports/{share_id}")
    async def get_shared_report(share_id: str):
        try:
            share_response = supabase.table("report_shares").select("*").eq("id", share_id).execute()
            if not share_response.data:
                raise HTTPException(status_code=404, detail="Share link not found")
            share = share_response.data[0]
                
            if share.get("revoked"):
                raise HTTPException(status_code=404, detail="Share link not found")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

        expires_at = share.get("expires_at")
        if expires_at:
            exp = datetime.fromisoformat(expires_at)
            if exp.tzinfo is None:
                exp = exp.replace(tzinfo=timezone.utc)
            if exp < datetime.now(timezone.utc):
                raise HTTPException(status_code=410, detail="Share link expired")

        try:
            report_response = supabase.table("ep_reports").select("*").eq("id", share["report_id"]).execute()
            if not report_response.data:
                raise HTTPException(status_code=404, detail="Report not found")
            report = report_response.data[0]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

        # Hide internal identifiers
        report.pop("user_id", None)
        return {"share": share, "report": report}

    return router