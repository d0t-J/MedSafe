from pydantic import BaseModel

class VisitorBootstrapRequest(BaseModel):
    visitor_id: str | None = None
    