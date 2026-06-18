import os
from importlib import import_module


FIELD_LABELS = {
    "indications_and_usage": "WHAT IS THIS DRUG FOR",
    "boxed_warning": "BLACK BOX WARNING (MOST SERIOUS)",
    "warnings": "WARNINGS",
    "contraindications": "WHO MUST NEVER TAKE THIS",
    "adverse_reactions": "SIDE EFFECTS",
    "drug_interactions": "DRUG INTERACTIONS",
    "do_not_use": "DO NOT USE IF",
    "ask_doctor": "ASK YOUR DOCTOR FIRST IF",
    "ask_doctor_or_pharmacist": "ASK YOUR DOCTOR OR PHARMACIST IF",
    "when_using": "WHILE TAKING THIS DRUG",
    "stop_use": "STOP USE AND SEE A DOCTOR IF",
    "pregnancy": "PREGNANCY AND BREASTFEEDING",
    "information_for_patients": "PATIENT INFORMATION",
    "dosage_and_administration": "DOSAGE",
}


def _get_client():
    """Build an Anthropic client only when analysis is requested."""
    try:
        anthropic = import_module("anthropic")
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "anthropic package is not installed. Install project dependencies first."
        ) from exc

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY is missing. Add it to your .env file.")

    return anthropic.Anthropic(api_key=api_key)


def build_drug_context(drug: dict) -> str:
    """Format one drug payload into model-friendly context text."""
    if not drug.get("found"):
        original = drug.get("original_name", "Unknown")
        normalized = drug.get("normalized_name", original)
        return (
            f"--- DRUG: {original} ---\n"
            f"STATUS: Not found in FDA database.\n"
            f"(Searched for: '{normalized}')\n"
        )

    brand = drug.get("brand_name", "N/A")
    generic = drug.get("generic_name", "N/A")

    sections = []
    for field_key, field_label in FIELD_LABELS.items():
        value = drug.get(field_key, "")
        if value:
            sections.append(f"{field_label}:\n{value[:2000]}")

    if not sections:
        sections.append("No detailed label information available.")

    return f"--- DRUG: {brand} (Generic: {generic}) ---\n" + "\n\n".join(sections)


def analyze_drug(drug: dict) -> str:
    """Analyze one drug summary with Claude."""
    client = _get_client()

    context = build_drug_context(drug)
    name = (
        drug.get("brand_name")
        or drug.get("normalized_name")
        or drug.get("original_name")
    )

    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1500,
        system="""You are MedSafe, a helpful medical information assistant. Your job is to help users understand the safety information of their medicine using official FDA drug label data.

Rules you must always follow:
1. Only use information from the FDA label data provided to you. Never invent or assume anything.
2. Always write in simple, plain English. Avoid medical jargon. If you must use a technical term, explain it in brackets.
3. Structure your response using only the sections where data is available. Possible sections are:
   - What Is This Drug For
   - Black Box Warning (if present — this is the most serious type of FDA warning)
   - Warnings
   - Who Must Never Take This
   - Side Effects
   - Drug Interactions
   - Do Not Use If
   - Ask Your Doctor First
   - While Taking This Drug
   - Stop Use And See A Doctor If
   - Pregnancy And Breastfeeding
   - Patient Information
   - Dosage
4. Always end your response with this exact disclaimer on its own line: "⚠️ This is for informational purposes only. Always consult your doctor or pharmacist before starting, stopping, or changing any medication."
5. If the drug was not found in the FDA database, say so clearly and suggest the user check the spelling.
6. Cite the drug label as your source (e.g., "According to the Warfarin Sodium label...").""",
        messages=[
            {
                "role": "user",
                "content": f"""Please analyze this medicine for the user: {name}

Here is the official FDA label data:

{context}

Please provide a clear plain English safety summary using the available sections.""",
            }
        ],
    )

    return message.content[0].text


def analyze_interaction(drug_list: list[dict]) -> str:
    """Analyze interactions across multiple drugs with Claude."""
    client = _get_client()

    all_contexts = []
    drug_names = []

    for drug in drug_list:
        all_contexts.append(build_drug_context(drug))
        name = (
            drug.get("brand_name")
            or drug.get("normalized_name")
            or drug.get("original_name")
        )
        drug_names.append(name)

    combined_context = "\n\n" + "=" * 50 + "\n\n".join(all_contexts)
    names_string = " and ".join(drug_names)

    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1000,
        system="""You are MedSafe, a medical interaction specialist. Your ONLY job in this response is to analyze potential interactions between the drugs provided.

Rules you must always follow:
1. ONLY analyze interactions between the drugs. Do not repeat individual drug side effects.
2. Only use information from the FDA label data provided. Never invent or assume anything.
3. Write in simple plain English. If you use a medical term explain it in brackets.
4. Structure your response exactly like this:
   - Start with one sentence stating whether a known interaction exists or not
   - If interaction exists: explain what happens when these drugs are taken together
   - If interaction exists: explain how serious it is
   - If interaction exists: explain what the user should do (e.g. consult doctor)
   - If no interaction data is found in the labels: say so clearly and still recommend consulting a doctor
5. Always end with this exact disclaimer: "⚠️ This is for informational purposes only. Always consult your doctor or pharmacist before taking these medicines together."
6. Keep your response concise and focused only on the interaction.""",
        messages=[
            {
                "role": "user",
                "content": f"""Analyze the potential drug interaction between: {names_string}

Here is the official FDA label data for each drug:

{combined_context}

Focus ONLY on how these drugs interact with each other. Do not repeat their individual side effects.""",
            }
        ],
    )

    return message.content[0].text


def analyze_drugs(drug_list: list[dict]) -> str:
    """Analyze one or more drugs and return a single plain-text summary."""
    if not drug_list:
        return (
            "No drug data was provided for analysis. "
            "Please enter at least one medicine name."
        )

    if len(drug_list) == 1:
        return analyze_drug(drug_list[0])

    sections = []
    for drug in drug_list:
        display_name = (
            drug.get("brand_name")
            or drug.get("normalized_name")
            or drug.get("original_name")
            or "Unknown Drug"
        )
        sections.append(f"{display_name}\n{analyze_drug(drug)}")

    sections.append("Drug Interaction Analysis\n" + analyze_interaction(drug_list))
    return "\n\n".join(sections)
