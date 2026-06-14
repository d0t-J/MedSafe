import uuid

from fastapi import APIRouter
from sqlalchemy.orm import Session

from core.database import SessionLocal
from models.user import User
from schemas.user import UserCreate


router = APIRouter(prefix="/api/users", tags=["users"])


@router.post("/")
def create_user(user: UserCreate):
    """Endpoint to create a new user"""
    db: Session = SessionLocal()

    try:
        db_user = User(
            id=str(uuid.uuid4()),
            name=user.name,
            email=user.email,
            password_hash=user.password,  # temp
        )

        db.add(db_user)
        db.commit()

        return {"message": "User created successfully"}
    finally:
        db.close()
