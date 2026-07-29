from pydantic import BaseModel

class AskRequest(BaseModel):
    book: str
    chapter: int
    question: str

class AskResponse(BaseModel):
    book: str
    chapter: int
    question: str