from pydantic import BaseModel

class FormResponse(BaseModel):
    results: list[dict] #