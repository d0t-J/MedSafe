from pydantic import BaseModel


class FirebaseTokenRequest(BaseModel):
    id_token: str


class FirebaseUserResponse(BaseModel):
    uid: str
    email: str | None = None
    name: str | None = None