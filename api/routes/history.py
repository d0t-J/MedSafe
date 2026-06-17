from fastapi import APIRouter, Header, HTTPException

from core.firebase import verify_firebase_id_token
from services.firestore.history_service import get_user_history

router = APIRouter(prefix="/api/history", tags=["history"])


@router.get("/")
def history(authorization: str | None = Header(default=None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing token")

    token = authorization.split(" ")[1]

    decoded = verify_firebase_id_token(token)

    uid = decoded["uid"]

    return get_user_history(uid)