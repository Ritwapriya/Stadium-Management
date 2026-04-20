import asyncio
import json
import logging
from typing import List
from fastapi import WebSocket
from redis.asyncio import Redis

logger = logging.getLogger(__name__)

class WebSocketManager:
    def __init__(self, redis_url: str):
        self.active_connections: List[WebSocket] = []
        self.redis = Redis.from_url(redis_url, decode_responses=True)
        self.pubsub = self.redis.pubsub()
        self.task = None

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error sending message to websocket: {e}")
                self.disconnect(connection)

    async def _listen_to_pubsub(self):
        # Subscribe to all output topics that the frontend cares about
        topics = ["crowd.density", "queue.predictions", "recommendations"]
        for topic in topics:
            await self.pubsub.subscribe(topic)
            
        logger.info(f"WebSocket Manager subscribed to Redis topics: {topics}")
        
        try:
            async for message in self.pubsub.listen():
                if message['type'] == 'message':
                    # Add topic metadata so frontend knows what data it's receiving
                    payload = {
                        "topic": message['channel'],
                        "data": json.loads(message['data'])
                    }
                    await self.broadcast(json.dumps(payload))
        except asyncio.CancelledError:
            pass
        except Exception as e:
           logger.error(f"WebSocket pubsub listener error: {e}")

    def start(self):
        if not self.task:
            self.task = asyncio.create_task(self._listen_to_pubsub())

    async def stop(self):
        if self.task:
            self.task.cancel()
            await self.pubsub.close()
            self.task = None
