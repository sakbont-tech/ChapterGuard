from pydantic import BaseModel, Field

class AskQuestion(BaseModel):
    book_id: str
    current_chapter: int = Field(ge=1)
    question: str

class AskResponse(BaseModel):
    book_id: str
    current_chapter: int
    question: str
    answer: str