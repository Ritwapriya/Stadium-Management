import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.bus.event_bus import EventBus
from backend.bus.shared_context import SharedContext
from backend.core.websocket_manager import WebSocketManager

from backend.agents.crowd_agent import CrowdAgent
from backend.agents.queue_agent import QueueAgent
from backend.agents.recommendation_agent import RecommendationAgent
from backend.agents.planner_agent import PlannerAgent
from backend.agents.chat_agent import ChatAgent

from backend.routers import context, recommend, chat, ws

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global instances
event_bus = EventBus(settings.REDIS_URL)
shared_context = SharedContext(settings.REDIS_URL)
ws_manager = WebSocketManager(settings.REDIS_URL)

crowd_agent = CrowdAgent(event_bus, shared_context)
queue_agent = QueueAgent(event_bus, shared_context)
recommend_agent = RecommendationAgent(event_bus, shared_context)
planner_agent = PlannerAgent(event_bus, shared_context)
chat_agent = ChatAgent(shared_context)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting EventBus...")
    event_bus.start()
    
    logger.info("Starting WebSocketManager...")
    ws_manager.start()

    logger.info("Starting Agents...")
    await crowd_agent.start()
    await queue_agent.start()
    await recommend_agent.start()
    planner_agent.start() # Background task

    yield

    # Shutdown
    logger.info("Shutting down...")
    await ws_manager.stop()
    await event_bus.stop()

app = FastAPI(title="Smart Stadium AI", lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(context.router, prefix="/context", tags=["Context"])
app.include_router(recommend.router, prefix="/recommend", tags=["Recommend"])
app.include_router(chat.router, prefix="/chat", tags=["Chat"])
app.include_router(ws.router, prefix="/ws", tags=["WebSocket"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=settings.PORT, reload=True)
