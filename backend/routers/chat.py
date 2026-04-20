from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class ChatRequest(BaseModel):
    query: str

@router.post("/")
async def chat_with_agent(request: ChatRequest):
    from backend.main import chat_agent
    
    response = await chat_agent.answer_query(request.query)
    return {"response": response}
