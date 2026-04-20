from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class RecommendRequest(BaseModel):
    user_id: str
    preference: str
    location: str

@router.post("/")
async def trigger_recommendation(request: RecommendRequest):
    from backend.main import event_bus
    
    # Just forward this user event to the bus!
    payload = request.model_dump()
    await event_bus.publish("user.context", payload)
    
    return {"status": "event published", "data": payload}
