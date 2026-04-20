import asyncio
import logging
from backend.bus.event_bus import EventBus
from backend.bus.shared_context import SharedContext

logger = logging.getLogger(__name__)

class QueueAgent:
    def __init__(self, event_bus: EventBus, shared_context: SharedContext):
        self.event_bus = event_bus
        self.shared_context = shared_context
        self.wait_times = {}

    async def process_queue_event(self, event_data: dict):
        """
        Processes incoming queue.raw data:
        {"stall": "food_A", "queue_length": 18, "service_rate": 2}
        """
        try:
            stall = event_data.get("stall")
            q_len = event_data.get("queue_length", 0)
            s_rate = event_data.get("service_rate", 1)  # people served per minute

            # Wait time formula W = L / μ
            wait_time_minutes = q_len / s_rate if s_rate > 0 else 0
            self.wait_times[stall] = round(wait_time_minutes, 1)

            # Identify flagged stalls (e.g. wait > 10 mins)
            flagged = [s for s, w in self.wait_times.items() if w > 10.0]

            output = {
                "wait_times": self.wait_times,
                "flagged": flagged
            }

            # 1. Write to Shared Context
            await self.shared_context.update_key("queue_state", output)

            # 2. Publish to Output Topic
            await self.event_bus.publish("queue.predictions", output)
            logger.debug(f"QueueAgent processed event for stall {stall}. Output published.")

        except Exception as e:
            logger.error(f"Error processing queue event: {e}")

    async def start(self):
        await self.event_bus.subscribe("queue.raw", self.process_queue_event)
        logger.info("QueueAgent started and listening to queue.raw")
