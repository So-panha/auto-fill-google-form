from pydantic import BaseModel, HttpUrl

class QuestionReq(BaseModel):
    url: HttpUrl