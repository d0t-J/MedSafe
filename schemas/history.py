from pydantic import BaseModel

class HistorySaveRequest(BaseModel):
    visitor_id: str
    drugs: list[str]
    analysis: str