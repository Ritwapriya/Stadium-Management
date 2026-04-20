import asyncio
import logging
from datetime import datetime, timezone
from backend.bus.event_bus import EventBus
from backend.bus.shared_context import SharedContext

logger = logging.getLogger(__name__)

class CrowdAgent:
    def __init__(self, event_bus: EventBus, shared_context: SharedContext):
        self.event_bus = event_bus
        self.shared_context = shared_context
        # We can store cumulative state if needed, but for now we process events live
        self.densities = {}

    async def get_density(self, count: int, capacity: int) -> float:
        if capacity <= 0:
            return 0.0
        return min(count / capacity, 1.0)

    async def process_sensor_event(self, event_data: dict):
        """
        Processes incoming sensor.raw data:
        {"zone": "A", "count": 412, "capacity": 500}
        """
        try:
            zone = event_data.get("zone")
            count = event_data.get("count", 0)
            capacity = event_data.get("capacity", 1)

            density = await self.get_density(count, capacity)
            self.densities[zone] = density

            # Determine hotspot
            hotspot = max(self.densities.keys(), key=lambda k: self.densities[k]) if self.densities else "Unknown"

            # 1. Update internal state
            output = {
                "zone_densities": self.densities,
                "hotspot": hotspot,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

            # 2. Write to Shared Context
            await self.shared_context.update_key("crowd_state", output)

            # 3. Publish to Output Topic
            await self.event_bus.publish("crowd.density", output)
            logger.debug(f"CrowdAgent processed event for zone {zone}. Output published.")

        except Exception as e:
            logger.error(f"Error processing crowd event: {e}")

    async def start(self):
        await self.event_bus.subscribe("sensor.raw", self.process_sensor_event)
        logger.info("CrowdAgent started and listening to sensor.raw")
