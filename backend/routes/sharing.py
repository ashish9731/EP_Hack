from fastapi import APIRouter, HTTPException, Cookie, Header
from typing import Optional
from datetime import datetime, timezone, timedelta
import uuid

from utils.auth import get_current_user

def create_sharing_router(supabase):
    router = APIRouter(tags=["sharing"])

    @router.post("/reports/{report_id}/share")
    async def create_report_share_link(
        report_id: str,
        session_token: Optional[str] = Cookie(None),
        authorization: Optional[str] = Header(None),
    ):
        user = await get_current_user(session_token, authorization)

        try:
            # Get Supabase client
            supabase_client = supabase
            
            # Check if report exists and belongs to the user
            report_response = supabase_client.table("reports").select("id").eq("id", report_id).eq("user_id", user["user_id"]).execute()
            
            if not report_response.data:
                raise HTTPException(status_code=404, detail="Report not found or not owned by user")

            share_id = f"share_{uuid.uuid4().hex}"
            now = datetime.now(timezone.utc)
            expires_at = now + timedelta(days=7)

            doc = {
                "id": share_id,
                "report_id": report_id,
                "owner_id": user["user_id"],
                "created_at": now.isoformat(),
                "expires_at": expires_at.isoformat(),
                "revoked": False,
            }

            # Save share link to Supabase
            response = supabase_client.table("shared_reports").insert(doc).execute()
            
            return {"share_id": share_id, "expires_at": expires_at.isoformat()}
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create share link: {str(e)}")

    @router.get("/shared/reports/{share_id}")
    async def get_shared_report(share_id: str):
        try:
            # Get Supabase client
            supabase_client = supabase
            
            # Query share link from Supabase
            share_response = supabase_client.table("shared_reports").select("*").eq("id", share_id).execute()
            
            if not share_response.data:
                raise HTTPException(status_code=404, detail="Share link not found")
                
            share = share_response.data[0]
            
            if share.get("revoked"):
                raise HTTPException(status_code=404, detail="Share link not found")

            expires_at = share.get("expires_at")
            if expires_at:
                exp = datetime.fromisoformat(expires_at)
                if exp.tzinfo is None:
                    exp = exp.replace(tzinfo=timezone.utc)
                if exp < datetime.now(timezone.utc):
                    raise HTTPException(status_code=410, detail="Share link expired")

            # Get the report from Supabase
            report_response = supabase_client.table("reports").select("*").eq("id", share["report_id"]).execute()
            
            if not report_response.data:
                raise HTTPException(status_code=404, detail="Report not found")
                
            report = report_response.data[0]

            # Hide internal identifiers
            report.pop("user_id", None)
            return {"share": share, "report": report}
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get shared report: {str(e)}")

    @router.delete("/reports/share/{share_id}")
    async def revoke_share_link(
        share_id: str,
        session_token: Optional[str] = Cookie(None),
        authorization: Optional[str] = Header(None),
    ):
        user = await get_current_user(session_token, authorization)

        try:
            # Get Supabase client
            supabase_client = supabase
            
            # Check if share link exists and belongs to the user
            share_response = supabase_client.table("shared_reports").select("id").eq("id", share_id).eq("owner_id", user["user_id"]).execute()
            
            if not share_response.data:
                raise HTTPException(status_code=404, detail="Share link not found or not owned by user")

            # Revoke the share link
            supabase_client.table("shared_reports").update({"revoked": True}).eq("id", share_id).execute()
            
            return {"message": "Share link revoked successfully"}
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to revoke share link: {str(e)}")

    return router