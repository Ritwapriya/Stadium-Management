import asyncio
import logging
from backend.bus.event_bus import EventBus
from backend.bus.shared_context import SharedContext

logger = logging.getLogger(__name__)

class RecommendationAgent:
    def __init__(self, event_bus: EventBus, shared_context: SharedContext):
        self.event_bus = event_bus
        self.shared_context = shared_context

    def trigger_staff_alert(self, message: str):
        # In a full system, this might push directly to a staff dashboard or pager.
        logger.warning(f"STAFF ALERT TRIGGERED: {message}")
        return message

    async def process_user_event(self, event_data: dict):
        """
        Reacts to new user.context events:
        {"user_id": "u001", "preference": "food", "location": "zone_B"}
        """
        try:
            preference = event_data.get("preference", "none")
            
            # 1. Get current shared context
            context = await self.shared_context.get_full_context()
            crowd_state = context.get("crowd_state") or {}
            queue_state = context.get("queue_state") or {}
            match_phase = context.get("match_phase") or "LIVE"
            
            # Simple heuristic based recommendation
            densities = crowd_state.get("zone_densities", {})
            wait_times = queue_state.get("wait_times", {})
            
            # Find the quietest food stall if preference is food
            action = "Enjoy the match!"
            confidence = 0.5
            reason = "Default recommendation."
            staff_alert = None
            
            if "wait_times" in queue_state:
                # Check for staff alerts
                for stall, wait in wait_times.items():
                    if wait > 10:
                        staff_alert = self.trigger_staff_alert(f"Open new counter at {stall} (Wait: {wait}m)")

            if preference == "food":
                if wait_times:
                     best_stall = min(wait_times.keys(), key=lambda k: wait_times[k])
                     min_wait = wait_times[best_stall]
                     
                     if match_phase == "HALFTIME":
                         action = f"Halftime Rush! {best_stall} still has lowest wait."
                         reason = f"Wait time is {min_wait}m despite halftime rush."
                         confidence = 0.75
                     else:
                         action = f"Head to {best_stall} for food."
                         reason = f"It currently has the shortest wait time ({min_wait}m)."
                         confidence = 0.85
                         
            elif preference == "wc":
                # Find the zone with least density
                if densities:
                    best_zone = min(densities.keys(), key=lambda k: densities[k])
                    action = f"Restrooms in {best_zone} are less crowded."
                    reason = f"Zone density is low ({densities[best_zone]:.2f})."
                    confidence = 0.90

            output = {
                "action": action,
                "confidence": confidence,
                "reason": reason,
                "match_phase": match_phase,
                "staff_alert": staff_alert
            }

            # 2. Write to Shared Context (update recommendations)
            await self.shared_context.update_key("recommendations", output)

            # 3. Publish to Output Topic
            await self.event_bus.publish("recommendations", output)
            logger.debug("RecommendationAgent processed user event and generated recommendation.")

        except Exception as e:
            logger.error(f"Error processing user context event: {e}")

    async def start(self):
        await self.event_bus.subscribe("user.context", self.process_user_event)
        logger.info("RecommendationAgent started and listening to user.context")
