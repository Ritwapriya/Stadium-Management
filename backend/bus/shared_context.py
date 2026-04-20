import json
from redis.asyncio import Redis
from typing import Dict, Any

class SharedContext:
    def __init__(self, redis_url: str):
        self.redis = Redis.from_url(redis_url, decode_responses=True)
        self.ttl = 30 # 30 seconds TTL for fast-changing context

    async def update_key(self, key: str, value: Any):
        await self.redis.set(key, json.dumps(value), ex=self.ttl)

    async def get_key(self, key: str) -> Any:
        data = await self.redis.get(key)
        return json.loads(data) if data else None

    async def get_full_context(self) -> Dict[str, Any]:
        """Returns a snapshot of the current shared context"""
        keys = ["crowd_state", "queue_state", "user_context", "match_phase", "plan", "recommendations"]
        context = {}
        for key in keys:
            context[key] = await self.get_key(key)
        return context
