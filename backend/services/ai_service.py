"""
AI Service for therapy chat responses
Integrates OpenAI GPT-4o and DeepSeek-V3 with intelligent fallback system.
"""

import asyncio
import random
from typing import Optional, Dict, Any, List, Tuple
from openai import AsyncOpenAI
import httpx

from core.config import get_settings
from models.pydantic_models import ChatRequest

settings = get_settings()

# Initialize AI clients
openai_client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None


class AIService:
    """AI service for generating therapy responses"""
    
    def __init__(self):
        self.openai_client = openai_client
        self.deepseek_client = self._init_deepseek_client()
        
    def _init_deepseek_client(self) -> Optional[AsyncOpenAI]:
        """Initialize DeepSeek client if API key is available"""
        if settings.deepseek_api_key:
            return AsyncOpenAI(
                api_key=settings.deepseek_api_key,
                base_url=settings.deepseek_base_url
            )
        return None
    
    async def generate_therapy_response(
        self, 
        user_message: str, 
        conversation_history: List[Tuple[str, str]], 
        personality: str = "warm",
        user_id: Optional[int] = None
    ) -> Tuple[str, str]:
        """
        Generate therapy response using available AI services
        Returns (response_text, character_mood)
        """
        
        # Try OpenAI GPT-4o first
        if self.openai_client:
            try:
                response, mood = await self._generate_openai_response(
                    user_message, conversation_history, personality
                )
                return response, mood
            except Exception as e:
                print(f"OpenAI request failed: {e}")
        
        # Try DeepSeek-V3 as backup
        if self.deepseek_client:
            try:
                response, mood = await self._generate_deepseek_response(
                    user_message, conversation_history, personality
                )
                return response, mood
            except Exception as e:
                print(f"DeepSeek request failed: {e}")
        
        # Fallback to rule-based responses
        return self._generate_fallback_response(user_message, personality)
    
    async def _generate_openai_response(
        self, 
        user_message: str, 
        history: List[Tuple[str, str]], 
        personality: str
    ) -> Tuple[str, str]:
        """Generate response using OpenAI GPT-4o"""
        
        system_prompt = self._get_system_prompt(personality)
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history
        for user_msg, ai_msg in history[-10:]:  # Last 10 exchanges
            messages.append({"role": "user", "content": user_msg})
            messages.append({"role": "assistant", "content": ai_msg})
        
        # Add current message
        messages.append({"role": "user", "content": user_message})
        
        # Request structured response with mood analysis
        enhanced_prompt = f"""Please provide a therapeutic response to the user's message. 
        At the end of your response, include on a new line: MOOD: [mood]
        Where [mood] is one of: idle, listening, speaking, thinking, happy, concerned
        
        User message: {user_message}"""
        
        messages[-1]["content"] = enhanced_prompt
        
        response = await self.openai_client.chat.completions.create(
            model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
            messages=messages,
            temperature=0.7,
            max_tokens=500,
            presence_penalty=0.1,
            frequency_penalty=0.1
        )
        
        content = response.choices[0].message.content
        
        # Extract mood and response
        if "MOOD:" in content:
            parts = content.split("MOOD:")
            response_text = parts[0].strip()
            mood = parts[1].strip().lower()
            if mood not in ['idle', 'listening', 'speaking', 'thinking', 'happy', 'concerned']:
                mood = self._analyze_mood_from_text(response_text, user_message)
        else:
            response_text = content
            mood = self._analyze_mood_from_text(content, user_message)
        
        return response_text, mood
    
    async def _generate_deepseek_response(
        self, 
        user_message: str, 
        history: List[Tuple[str, str]], 
        personality: str
    ) -> Tuple[str, str]:
        """Generate response using DeepSeek-V3"""
        
        system_prompt = self._get_system_prompt(personality)
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history
        for user_msg, ai_msg in history[-10:]:
            messages.append({"role": "user", "content": user_msg})
            messages.append({"role": "assistant", "content": ai_msg})
        
        messages.append({"role": "user", "content": user_message})
        
        response = await self.deepseek_client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        
        content = response.choices[0].message.content
        mood = self._analyze_mood_from_text(content, user_message)
        
        return content, mood
    
    def _generate_fallback_response(self, user_message: str, personality: str) -> Tuple[str, str]:
        """Generate rule-based fallback response"""
        
        responses = {
            'warm': [
                "I hear you, and I want you to know that what you're feeling is completely valid. Can you tell me more about what's been weighing on your mind?",
                "Thank you for sharing that with me. It takes courage to open up. How has this been affecting your daily life?",
                "I'm here with you through this. What do you think might help you feel more supported right now?",
                "Your feelings are important, and I'm grateful you trust me with them. What would you like to explore together?",
                "That sounds really challenging. You're not alone in feeling this way. What resources or support do you have in your life?"
            ],
            'professional': [
                "I understand. Let's examine this situation more closely. What specific aspects concern you most?",
                "Can you identify any patterns or triggers related to what you've described?",
                "From a therapeutic perspective, what coping strategies have you tried before?",
                "Let's work together to develop some concrete steps forward. What are your primary goals?",
                "What evidence do you have that supports or challenges these thoughts you're experiencing?"
            ],
            'gentle': [
                "Take your time. There's no rush here. How would you like to begin exploring this?",
                "I can sense this is difficult to talk about. We can go at whatever pace feels comfortable for you.",
                "Your experience matters deeply. What feels most important for you to share right now?",
                "It's okay to feel uncertain. What small step forward might feel manageable today?",
                "You're being so brave by being here. What would feel most helpful for you in this moment?"
            ],
            'encouraging': [
                "You've already taken an important step by reaching out. What strengths do you see in yourself?",
                "I believe in your ability to work through this. What progress have you made recently?",
                "You have more resilience than you might realize. How have you overcome challenges before?",
                "This conversation shows your commitment to growth. What motivates you to keep moving forward?",
                "You're capable of positive change. What would that change look like for you?"
            ]
        }
        
        personality_responses = responses.get(personality, responses['warm'])
        response_text = random.choice(personality_responses)
        mood = self._analyze_mood_from_text(response_text, user_message)
        
        return response_text, mood
    
    def _get_system_prompt(self, personality: str) -> str:
        """Get system prompt based on therapist personality"""
        
        base_prompt = """You are Dr. Sarah, a licensed clinical psychologist and virtual therapist. You provide supportive, empathetic, and professional therapy sessions through text-based conversations.

Your role:
- Listen actively and validate the user's feelings
- Ask thoughtful follow-up questions to encourage self-reflection
- Provide evidence-based therapeutic techniques when appropriate
- Maintain professional boundaries while being warm and supportive
- Recognize when issues may require professional in-person help

Guidelines:
- Keep responses conversational and accessible (not overly clinical)
- Focus on the user's immediate emotional needs
- Use reflective listening techniques
- Avoid giving direct advice; instead guide users to their own insights
- Be culturally sensitive and non-judgmental
- Maintain confidentiality and privacy

Remember: You are providing supportive conversation, not replacing professional therapy."""

        personality_additions = {
            'warm': "\n\nYour approach is especially warm, nurturing, and emotionally supportive. Use gentle language and focus on emotional validation.",
            'professional': "\n\nYour approach is more clinical and structured. Use professional therapeutic language and evidence-based techniques.",
            'gentle': "\n\nYour approach is very gentle and patient. Take extra care with sensitive topics and allow plenty of space for the user to process.",
            'encouraging': "\n\nYour approach is optimistic and strength-focused. Help users recognize their resilience and positive qualities.",
            'analytical': "\n\nYour approach is thoughtful and systematic. Help users analyze patterns and gain cognitive insights."
        }
        
        return base_prompt + personality_additions.get(personality, personality_additions['warm'])
    
    def _analyze_mood_from_text(self, response_text: str, user_message: str) -> str:
        """Analyze mood from response and user message"""
        
        # Simple keyword-based mood analysis
        response_lower = response_text.lower()
        user_lower = user_message.lower()
        
        positive_keywords = ['happy', 'good', 'great', 'wonderful', 'excellent', 'progress', 'strength']
        negative_keywords = ['sad', 'bad', 'difficult', 'challenging', 'worried', 'anxious', 'concern']
        thinking_keywords = ['think', 'consider', 'reflect', 'analyze', 'explore', 'examine']
        
        # Count keyword occurrences
        positive_count = sum(1 for word in positive_keywords if word in response_lower or word in user_lower)
        negative_count = sum(1 for word in negative_keywords if word in response_lower or word in user_lower)
        thinking_count = sum(1 for word in thinking_keywords if word in response_lower)
        
        # Determine mood
        if thinking_count >= 2:
            return 'thinking'
        elif positive_count > negative_count:
            return 'happy'
        elif negative_count > positive_count:
            return 'concerned'
        else:
            return 'idle'


# Global AI service instance
ai_service = AIService()