from pydantic import BaseModel


class DrugCheckRequest(BaseModel):
    drugs: list[str]
