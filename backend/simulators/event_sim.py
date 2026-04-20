import asyncio
import json
import random
from redis.asyncio import Redis

async def main():
    redis = Redis.from_url("redis://localhost:6379", decode_responses=True)
    users = ["u001", "u002", "u003"]
    preferences = ["food", "wc", "none"]
    locations = ["North Gate", "East Stand"]
    
    print("Started Event/User Simulator...")
    while True:
        try:
            payload = {
                "user_id": random.choice(users),
                "preference": random.choice(preferences),
                "location": random.choice(locations)
            }
            
            await redis.publish("user.context", json.dumps(payload))
            print(f"Published to user.context: {payload}")
            
            await asyncio.sleep(5)
        except Exception as e:
            print(f"Error in event sim: {e}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
