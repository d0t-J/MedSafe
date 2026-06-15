import uuid

from fastapi import APIRouter
from sqlalchemy.orm import Session

from core.database import SessionLocal
from repositories.visitor import get_visitor, create_visitor
from repositories.drug_check import create_drug_check, get_history_for_visitor
from schemas.visitor import VisitorBootstrapRequest

router = APIRouter(prefix="/visitors", tags=["Visitors"])


@router.post("/bootstrap")
def bootstrap_visitor(payload: VisitorBootstrapRequest):
    db: Session = SessionLocal()

    try:
        visitor_id = payload.visitor_id or str(uuid.uuid4())

        visitor = get_visitor(db, visitor_id)
        if visitor is None:
            visitor = create_visitor(db, visitor_id)
        return {"visitor_id": visitor.id, "message": "Visitor ready"}
    finally:
        db.close()
