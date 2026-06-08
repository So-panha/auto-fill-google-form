from pydantic import BaseModel, Field

class QuestionInfo(BaseModel):
    title: str
    entry: int
    question_info: str | None = None
    options: list[str] = Field(default_factory=list)