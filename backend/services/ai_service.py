"""
AI Service for therapy chat responses
Integrates OpenAI GPT-4o and DeepSeek-V3 with intelligent fallback system.
"""

import logging
from services.local_llm_service import local_llm_service

class AIService:
    """AI service for generating therapy responses using local LLM"""
    def __init__(self):
        self.local_llm_service = local_llm_service

    async def generate_therapy_response(
        self,
        user_message: str,
        conversation_history,
        personality: str = "warm",
        user_id=None
    ):
        logging.info(f"[AIService] Generating response for user_id={user_id}, personality={personality}, message='{user_message}'")
        response, mood = self.local_llm_service.generate_therapy_response(user_message, conversation_history, personality, user_id)
        logging.info(f"[AIService] Local LLM response: '{response}' | mood: {mood}")
        return response, mood

ai_service = AIService()