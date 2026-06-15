from pydantic import BaseModel


class DrugCheckRequest(BaseModel):
    drugs: list[str]
    visitor_id: str | None = None
