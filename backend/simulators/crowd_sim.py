import asyncio
import json
import random
from redis.asyncio import Redis

async def main():
    redis = Redis.from_url("redis://localhost:6379", decode_responses=True)
    zones = ["North Gate", "South Gate", "East Stand", "West Stand", "Food Court"]
    
    print("Started Crowd Simulator...")
    while True:
        try:
            zone = random.choice(zones)
            # Simulate a changing crowd
            count = random.randint(100, 500)
            capacity = 500
            
            payload = {
                "zone": zone,
                "count": count,
                "capacity": capacity
            }
            
            await redis.publish("sensor.raw", json.dumps(payload))
            print(f"Published to sensor.raw: {payload}")
            
            await asyncio.sleep(2)
        except Exception as e:
            print(f"Error in crowd sim: {e}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
