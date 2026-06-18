from firebase_admin import firestore
from core.firebase import get_firestore_client


def upsert_user_profile(uid: str, email: str, name: str = None):
    """Create or update a user profile in Firestore."""
    db = get_firestore_client()

    user_data = {
        "uid": uid,
        "email": email,
        "name": name,
        "updated_at": firestore.SERVER_TIMESTAMP,
    }

    doc_ref = db.collection("users").document(uid)

    if not doc_ref.get().exists:
        user_data["created_at"] = firestore.SERVER_TIMESTAMP
        user_data["search_count"] = 0

    doc_ref.set(user_data, merge=True)