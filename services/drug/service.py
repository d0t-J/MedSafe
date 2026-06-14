import httpx


def normalize_drug_name(drug_name: str) -> str:
    """Normalize a drug name using RxNorm as a fallback helper."""
    url = f"https://rxnav.nlm.nih.gov/REST/spellingsuggestions.json?name={drug_name}"

    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(url)
            data = response.json()

            suggestions = (
                data.get("suggestionGroup", {})
                .get("suggestionList", {})
                .get("suggestion", [])
            )

            if suggestions:
                return suggestions[0]
            return drug_name

    except Exception:
        return drug_name


def search_fda(client: httpx.Client, drug_name: str):
    """Search OpenFDA for one drug and return the first matching record."""

    human_filter = (
        'openfda.product_type:"HUMAN+OTC+DRUG"+'
        'OR+openfda.product_type:"HUMAN+PRESCRIPTION+DRUG"'
    )

    specific_url = (
        f"https://api.fda.gov/drug/label.json?"
        f'search=(openfda.brand_name:"{drug_name}"+'
        f'OR+openfda.generic_name:"{drug_name}")'
        f"+AND+({human_filter})&limit=1"
    )

    try:
        response = client.get(specific_url)
        data = response.json()
        if data.get("results"):
            return data["results"][0]
    except Exception:
        pass

    broad_url = (
        f"https://api.fda.gov/drug/label.json?"
        f'search=("{drug_name}")+AND+({human_filter})&limit=1'
    )

    try:
        response = client.get(broad_url)
        data = response.json()
        if data.get("results"):
            return data["results"][0]
    except Exception:
        pass

    last_resort_url = (
        f'https://api.fda.gov/drug/label.json?search="{drug_name}"&limit=1'
    )

    try:
        response = client.get(last_resort_url)
        data = response.json()
        if data.get("results"):
            return data["results"][0]
    except Exception:
        pass

    return None


def fetch_fda_label(drug_name: str) -> dict:
    """Fetch and normalize label fields for a single drug."""

    with httpx.Client(timeout=15.0) as client:
        result = search_fda(client, drug_name)
        name_used = drug_name

        if result is None:
            normalized_name = normalize_drug_name(drug_name)
            if normalized_name.lower() != drug_name.lower():
                result = search_fda(client, normalized_name)
                name_used = normalized_name

        if result is None:
            return {
                "found": False,
                "original_name": drug_name,
                "normalized_name": name_used,
            }

        def extract_field(field_name):
            value = result.get(field_name, [])
            if isinstance(value, list):
                return " ".join(value).strip()
            return str(value).strip() if value else ""

        def extract_either(primary_field, fallback_field):
            value = extract_field(primary_field)
            if value:
                return value
            return extract_field(fallback_field)

        openfda = result.get("openfda", {})
        brand_names = openfda.get("brand_name", [])
        generic_names = openfda.get("generic_name", [])

        return {
            "found": True,
            "original_name": drug_name,
            "normalized_name": name_used,
            "brand_name": brand_names[0] if brand_names else name_used,
            "generic_name": generic_names[0] if generic_names else name_used,
            "indications_and_usage": extract_field("indications_and_usage"),
            "boxed_warning": extract_field("boxed_warning"),
            "warnings": extract_either("warnings", "warnings_and_cautions"),
            "contraindications": extract_field("contraindications"),
            "adverse_reactions": extract_field("adverse_reactions"),
            "drug_interactions": extract_field("drug_interactions"),
            "do_not_use": extract_field("do_not_use"),
            "ask_doctor": extract_field("ask_doctor"),
            "ask_doctor_or_pharmacist": extract_field("ask_doctor_or_pharmacist"),
            "when_using": extract_field("when_using"),
            "stop_use": extract_field("stop_use"),
            "pregnancy": extract_either("pregnancy_or_breast_feeding", "pregnancy"),
            "information_for_patients": extract_field("information_for_patients"),
            "dosage_and_administration": extract_field("dosage_and_administration"),
        }


def fetch_multiple_drugs(drug_names: list[str]) -> list[dict]:
    """Fetch FDA data for multiple drugs in sequence."""
    return [fetch_fda_label(name) for name in drug_names]
