from fastapi import APIRouter, HTTPException

from schemas.drug import DrugCheckRequest
from services.drug.service import fetch_multiple_drugs
from services.ai.service import analyze_drugs

router = APIRouter(prefix="/api", tags=["drug-check"])


@router.post("/check")
def check_drugs(request: DrugCheckRequest):
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

    return {"analysis": analysis, "drug_data": drug_data}
