import asyncio
import json
import random
from redis.asyncio import Redis

async def main():
    redis = Redis.from_url("redis://localhost:6379", decode_responses=True)
    stalls = ["Burger Stand", "Pizza Corner", "Beer Tent", "Restroom North"]
    
    print("Started Queue Simulator...")
    while True:
        try:
            stall = random.choice(stalls)
            
            # Service rate: people served per minute
            service_rate = random.randint(1, 5)
            # Queue length changes
            queue_length = random.randint(0, 50)
            
            payload = {
                "stall": stall,
                "queue_length": queue_length,
                "service_rate": service_rate
            }
            
            # Publish to queue.raw (NOT sensor.raw)
            await redis.publish("queue.raw", json.dumps(payload))
            print(f"Published to queue.raw: {payload}")
            
            await asyncio.sleep(3)
        except Exception as e:
            print(f"Error in queue sim: {e}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
