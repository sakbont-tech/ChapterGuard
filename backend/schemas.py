from pydantic import BaseModel

class AskRequest(BaseModel):
    title: str
    chapter: int
    question: str

class AskResponse(BaseModel):
    title: str
    chapter: int
    question: str
    response: str