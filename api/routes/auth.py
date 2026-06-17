from fastapi import APIRouter, HTTPException
from core.firebase import verify_firebase_id_token
from schemas.auth import FirebaseTokenRequest, FirebaseUserResponse
from services.firestore.profile_service import upsert_user_profile

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/verify", response_model=FirebaseUserResponse)
def verify_token(payload: FirebaseTokenRequest):
    try:
        decoded = verify_firebase_id_token(payload.id_token)
    except Exception as exc:
        raise HTTPException(status_code=401, detail=f"Invalid Firebase token: {exc}")

    uid = decoded.get("uid")
    email = decoded.get("email")
    name = decoded.get("name")

    upsert_user_profile(uid=uid, email=email, name=name)

    return {"uid": uid, "email": email, "name": name}