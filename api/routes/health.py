from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
def health_check():
    """Simple check to confirm the server is alive and running."""
    return {"status": "ok", "message": "MedSafe API is running!"}
