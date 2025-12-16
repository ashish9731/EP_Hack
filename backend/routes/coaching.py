from fastapi import APIRouter, Cookie, Header, HTTPException
from typing import Optional
from datetime import datetime, timezone
import uuid

from utils.auth import get_current_user

def create_coaching_router(supabase):
    router = APIRouter(prefix="/coaching", tags=["coaching"])

    @router.post("/requests")
    async def create_coaching_request(
        payload: dict,
        session_token: Optional[str] = Cookie(None),
        authorization: Optional[str] = Header(None),
    ):
        user = get_current_user(session_token, authorization)

        try:
            # Get Supabase client
            supabase_client = supabase()
            
            now = datetime.now(timezone.utc).isoformat()
            req_id = f"coachreq_{uuid.uuid4().hex}"

            doc = {
                "id": req_id,
                "user_id": user["user_id"],
                "name": payload.get("name"),
                "email": payload.get("email"),
                "goal": payload.get("goal"),
                "preferred_times": payload.get("preferred_times"),
                "notes": payload.get("notes"),
                "report_id": payload.get("report_id"),
                "status": "new",
                "created_at": now,
                "updated_at": now,
            }

            # Save coaching request to Supabase
            response = supabase_client.table("coaching_requests").insert(doc).execute()
            
            return {"request_id": req_id}
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create coaching request: {str(e)}")

    @router.get("/requests")
    async def list_coaching_requests(
        session_token: Optional[str] = Cookie(None),
        authorization: Optional[str] = Header(None),
    ):
        user = get_current_user(session_token, authorization)

        try:
            # Get Supabase client
            supabase_client = supabase()
            
            # Query coaching requests from Supabase
            response = supabase_client.table("coaching_requests").select("*").eq("user_id", user["user_id"]).order("created_at", desc=True).execute()
            
            requests = response.data if response.data else []
            return {"requests": requests}
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to list coaching requests: {str(e)}")

    return router