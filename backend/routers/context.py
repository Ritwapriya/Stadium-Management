from fastapi import APIRouter, Depends
from backend.bus.shared_context import SharedContext

router = APIRouter()

# Dependency to get shared_context (usually set in app state)
def get_shared_context():
    pass # Will be overridden in main.py or passed explicitly

@router.get("/")
async def get_context():
    from backend.main import shared_context
    context = await shared_context.get_full_context()
    return context
