from fastapi import APIRouter, HTTPException, Cookie, Header
from typing import Optional
from datetime import datetime, timezone, timedelta
import uuid

from utils.auth import get_current_user


def create_sharing_router(db):
    router = APIRouter(tags=["sharing"])

    @router.post("/reports/{report_id}/share")
    async def create_report_share_link(
        report_id: str,
        session_token: Optional[str] = Cookie(None),
        authorization: Optional[str] = Header(None),
    ):
        user = await get_current_user(db, session_token, authorization)

        report = await db.ep_reports.find_one(
            {"report_id": report_id, "user_id": user["user_id"]},
            {"_id": 0},
        )
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")

        share_id = f"share_{uuid.uuid4().hex}"
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(days=7)

        doc = {
            "share_id": share_id,
            "report_id": report_id,
            "owner_user_id": user["user_id"],
            "created_at": now.isoformat(),
            "expires_at": expires_at.isoformat(),
            "revoked": False,
        }

        await db.report_shares.insert_one(doc)
        return {"share_id": share_id, "expires_at": expires_at.isoformat()}

    @router.get("/shared/reports/{share_id}")
    async def get_shared_report(share_id: str):
        share = await db.report_shares.find_one({"share_id": share_id}, {"_id": 0})
        if not share or share.get("revoked"):
            raise HTTPException(status_code=404, detail="Share link not found")

        expires_at = share.get("expires_at")
        if expires_at:
            exp = datetime.fromisoformat(expires_at)
            if exp.tzinfo is None:
                exp = exp.replace(tzinfo=timezone.utc)
            if exp < datetime.now(timezone.utc):
                raise HTTPException(status_code=410, detail="Share link expired")

        report = await db.ep_reports.find_one({"report_id": share["report_id"]}, {"_id": 0})
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")

        # Hide internal identifiers
        report.pop("user_id", None)
        return {"share": share, "report": report}

    return router
