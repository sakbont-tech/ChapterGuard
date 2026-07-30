from pydantic import BaseModel, Field

class AskRequest(BaseModel):
    title: str
    chapter: int = Field(ge=1)
    question: str

class AskResponse(BaseModel):
    title: str
    chapter: int
    question: str
    response: str