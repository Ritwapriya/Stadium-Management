import logging
import asyncio
import json
from typing import List, Callable, Dict, Any
from redis.asyncio import Redis

logger = logging.getLogger(__name__)

class EventBus:
    def __init__(self, redis_url: str):
        self.redis = Redis.from_url(redis_url, decode_responses=True)
        self.pubsub = self.redis.pubsub()
        self.subscribers = {}
        self.task = None

    async def publish(self, topic: str, payload: Dict[str, Any]):
        try:
            message = json.dumps(payload)
            await self.redis.publish(topic, message)
        except Exception as e:
            logger.error(f"Failed to publish to {topic}: {e}")

    async def subscribe(self, topic: str, callback: Callable):
        if topic not in self.subscribers:
            self.subscribers[topic] = []
            await self.pubsub.subscribe(topic)
        self.subscribers[topic].append(callback)

    async def _listen(self):
        try:
            async for message in self.pubsub.listen():
                if message['type'] == 'message':
                    topic = message['channel']
                    if topic in self.subscribers:
                        try:
                            data = json.loads(message['data'])
                            for callback in self.subscribers[topic]:
                                asyncio.create_task(callback(data))
                        except json.JSONDecodeError:
                            logger.error(f"Failed to decode message on topic {topic}")
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Error in EventBus listener: {e}")

    def start(self):
        if not self.task:
             self.task = asyncio.create_task(self._listen())

    async def stop(self):
        if self.task:
            self.task.cancel()
            await self.pubsub.close()
            self.task = None

