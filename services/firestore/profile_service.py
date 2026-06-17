import os
from functools import lru_cache

import firebase_admin
from firebase_admin import auth, credentials, firestore
from dotenv import load_dotenv

load_dotenv()


@lru_cache(maxsize=1)
def initialize_firebase():
    if firebase_admin._apps:
        return firebase_admin.get_app()

    project_id = os.getenv("FIREBASE_PROJECT_ID")
    client_email = os.getenv("FIREBASE_CLIENT_EMAIL")
    private_key = os.getenv("FIREBASE_PRIVATE_KEY", "").replace("\\n", "\n")

    if not all([project_id, client_email, private_key]):
        missing = [k for k, v in [("project_id", project_id), ("client_email", client_email), ("private_key", private_key)] if not v]
        raise RuntimeError(f"Missing Firebase credentials: {', '.join(missing)}")

    cred = credentials.Certificate(
        {
            "type": "service_account",
            "project_id": project_id,
            "client_email": client_email,
            "private_key": private_key,
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    )

    return firebase_admin.initialize_app(cred)


def get_firestore_client():
    initialize_firebase()
    return firestore.client()


def verify_firebase_id_token(id_token: str):
    try:
        initialize_firebase()
        return auth.verify_id_token(id_token)
    except auth.ExpiredSignatureError:
        raise ValueError("Token expired")
    except auth.InvalidSignatureError:
        raise ValueError("Invalid token")
    except Exception as e:
        raise ValueError(f"Token verification failed: {str(e)}")
    

def upsert_user_profile(uid: str, email: str, name: str = None):
    """Create or update a user profile in Firestore."""
    db = get_firestore_client()
    user_data = {
        "email": email,
    }
    if name:
        user_data["name"] = name
    
    db.collection("users").document(uid).set(user_data, merge=True)