from firebase_admin import firestore
from core.firebase import get_firestore_client


def save_user_history(uid: str, drugs: list[str], analysis: str):
    db = get_firestore_client()
    db.collection("users").document(uid).collection("history").add(
        {
            "drugs": drugs,
            "analysis": analysis,
            "created_at": firestore.SERVER_TIMESTAMP,
        }
    )


def get_user_history(uid: str, limit: int = 20):
    db = get_firestore_client()
    docs = (
        db.collection("users")
        .document(uid)
        .collection("history")
        .order_by("created_at", direction=firestore.Query.DESCENDING)
        .limit(limit)
        .stream()
    )

    results = []
    for doc in docs:
        item = doc.to_dict()
        item["id"] = doc.id
        results.append(item)
    return results

def increment_search_count(uid: str):
    db = get_firestore_client()

    db.collection("users").document(uid).update(
        {
            "search_count": firestore.Increment(1)
        }
    )