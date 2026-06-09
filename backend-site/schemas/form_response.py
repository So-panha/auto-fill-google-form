from pydantic import BaseModel

class FormResponse(BaseModel):
    results: dict