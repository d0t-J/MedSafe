from fastapi import APIRouter, HTTPException, Header

from schemas.drug import DrugCheckRequest
from services.drug.service import fetch_multiple_drugs
from services.ai.service import analyze_drugs
from core.firebase import verify_firebase_id_token
from services.firestore.history_service import save_user_history, increment_search_count
from services.firestore.profile_service import upsert_user_profile

router = APIRouter(prefix="/api", tags=["drug-check"])


@router.post("/check")
def check_drugs(request: DrugCheckRequest, authorization: str | None = Header(default=None)):
    """Main endpoint for single and multi-drug safety checks."""
    if len(request.drugs) == 0:
        raise HTTPException(
            status_code=400, detail="Please provide at least one drug name."
        )

    if len(request.drugs) > 5:
        raise HTTPException(
            status_code=400,
            detail="Please provide no more than 5 drug names at a time.",
        )

    cleaned_drugs = [name.strip() for name in request.drugs if name.strip()]
    if not cleaned_drugs:
        raise HTTPException(
            status_code=400, detail="No valid drug names were provided."
        )

    try:
        drug_data = fetch_multiple_drugs(cleaned_drugs)
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Failed to fetch drug data from FDA. Please try again. Error: {str(exc)}",
        ) from exc

    try:
        analysis = analyze_drugs(drug_data)
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Failed to get AI analysis. Please try again. Error: {str(exc)}",
        ) from exc

    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        try:
            decoded = verify_firebase_id_token(token)
            uid = decoded.get("uid")
            email = decoded.get("email")
            name = decoded.get("name")
            upsert_user_profile(uid=uid, email=email, name=name)
            save_user_history(uid=uid, drugs=cleaned_drugs, analysis=analysis)
            increment_search_count(uid)
        except Exception as exc:
            print(f"Firestore save failed: {exc}")
    return {"analysis": analysis, "drug_data": drug_data}
