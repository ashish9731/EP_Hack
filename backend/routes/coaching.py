from fastapi import APIRouter, Cookie, Header
from typing import Optional
from datetime import datetime, timezone
import uuid

from utils.auth import get_current_user


def create_coaching_router(db):
    router = APIRouter(prefix="/coaching", tags=["coaching"])

    @router.post("/requests")
    async def create_coaching_request(
        payload: dict,
        session_token: Optional[str] = Cookie(None),
        authorization: Optional[str] = Header(None),
    ):
        user = await get_current_user(db, session_token, authorization)

        now = datetime.now(timezone.utc).isoformat()
        req_id = f"coachreq_{uuid.uuid4().hex}"

        doc = {
            "request_id": req_id,
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

        await db.coaching_requests.insert_one(doc)
        return {"request_id": req_id}

    return router
