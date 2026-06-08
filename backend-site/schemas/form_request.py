from fastapi import UploadFile, File
from pydantic import BaseModel

from pydantic import BaseModel, Field

class FormRequest(BaseModel):
    url: str = Field(..., description="Google Form prefill URL")
    number: int = Field(..., description="Number of submissions")