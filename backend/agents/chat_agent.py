import logging
import json
import google.generativeai as genai
from backend.bus.shared_context import SharedContext
from backend.config import settings

logger = logging.getLogger(__name__)

class ChatAgent:
    def __init__(self, shared_context: SharedContext):
        self.shared_context = shared_context
        
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
        else:
            self.model = None
            logger.warning("GEMINI_API_KEY not set. Chat agent will use fallback responses.")

    async def answer_query(self, query: str) -> str:
        """
        Answers a user query using the latest shared context without re-computing state.
        """
        # Read merged shared context
        context = await self.shared_context.get_full_context()
        
        system_prompt = f"""
        You are a helpful smart stadium AI assistant. You help attendees navigate the stadium, find food, and avoid crowds.
        
        Current Live Stadium Context:
        {json.dumps(context, indent=2)}
        
        Answer the user's question concisely based ONLY on this provided context. If the context doesn't have the answer, say so.
        Current match phase is {context.get('match_phase', 'Unknown')}.
        """
        
        if not self.model:
             return "I'm sorry, I am currently offline because the Gemini API key is missing."
             
        try:
             # Depending on Gemini API version, chat might require a different structure. 
             # Simple generate_content for now
             response = self.model.generate_content(
                f"{system_prompt}\n\nUser Question: {query}"
             )
             return response.text
        except Exception as e:
             logger.error(f"Gemini API error: {e}")
             return "Sorry, I am having trouble connecting to my brain right now."
