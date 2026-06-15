from sqlalchemy.orm import Session
from models.drug_check import DrugCheck


def create_drug_check(db: Session, visitor_id: str, drugs: dict, analysis: str):
    drug_record = DrugCheck(
        visitor_id=visitor_id, drugs={"drugs": drugs}, analysis=analysis
    )
    db.add(drug_record)
    db.commit()
    db.refresh(drug_record)
    return drug_record


def get_history_for_visitor(db: Session, visitor_id: str, limit: int = 20):
    return (
        db.query(DrugCheck)
        .filter(DrugCheck.visitor_id == visitor_id)
        .order_by(DrugCheck.created_at.desc())
        .limit(limit)
        .all()
    )
