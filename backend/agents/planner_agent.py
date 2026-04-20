import asyncio
import logging
from backend.bus.event_bus import EventBus
from backend.bus.shared_context import SharedContext

logger = logging.getLogger(__name__)

class PlannerAgent:
    def __init__(self, event_bus: EventBus, shared_context: SharedContext):
        self.event_bus = event_bus
        self.shared_context = shared_context

    async def generate_plan(self):
        """
        Periodically checks the shared context and generates an optimized plan sequence.
        """
        while True:
            try:
                 context = await self.shared_context.get_full_context()
                 match_phase = context.get("match_phase") or "PRE"
                 
                 plan = []
                 if match_phase == "PRE":
                     plan = [
                         {"action": "Enter via Gate B", "confidence": 0.85},
                         {"action": "Grab merch before lines build", "confidence": 0.70}
                     ]
                 elif match_phase == "LIVE":
                     plan = [
                         {"action": "Watch match", "confidence": 0.95},
                         {"action": "Order food to seat", "confidence": 0.60}
                     ]
                 elif match_phase == "HALFTIME":
                     plan = [
                         {"action": "Avoid food queues, wait 5 mins", "confidence": 0.80},
                         {"action": "Visit nearest WC", "confidence": 0.75}
                     ]
                 elif match_phase == "POST":
                     plan = [
                         {"action": "Exit via South Gate", "confidence": 0.90},
                         {"action": "Book rideshare from Zone C", "confidence": 0.85}
                     ]
                     
                 output = {"current_phase": match_phase, "plan_sequence": plan}
                 
                 # Store in context
                 await self.shared_context.update_key("plan", output)
                 
                 # Optionally publish if frontend needs it immediately via stream
                 await self.event_bus.publish("plan.update", output)
                 
            except Exception as e:
                logger.error(f"Planner error: {e}")
            
            # Re-evaluate plan every 15 seconds
            await asyncio.sleep(15)

    def start(self):
         asyncio.create_task(self.generate_plan())
         logger.info("PlannerAgent started background planning loop")
