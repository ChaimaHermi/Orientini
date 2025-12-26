from pydantic import BaseModel

# request
class QuestionRequest(BaseModel):
    question: str

class AnswerResponse(BaseModel):
    answer: str