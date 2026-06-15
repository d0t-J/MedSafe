from sqlalchemy.orm import Session
from models.visitor import Visitor


def get_visitor(db: Session, visitor_id: str):
    return db.query(Visitor).filter(Visitor.id == visitor_id).first()


def create_visitor(db: Session, visitor_id: str):
    visitor = Visitor(id=visitor_id)
    db.add(visitor)
    db.commit()
    db.refresh(visitor)
    return visitor
