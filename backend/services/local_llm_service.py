import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from core.config import get_settings
import logging

settings = get_settings()

class LocalLLMService:
    def __init__(self, model_id):
        self.model_id = model_id
        self.tokenizer = None
        self.model = None
        self.is_initialized = False
        self.initialize_model()
    
    def initialize_model(self):
        """Initialize the model with error handling"""
        try:
            logging.info(f"[LocalLLMService] Initializing model: {self.model_id}")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_id,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
            )
            self.model.to("cuda" if torch.cuda.is_available() else "cpu")
            self.is_initialized = True
            logging.info(f"[LocalLLMService] Model initialized successfully on {self.model.device}")
        except Exception as e:
            logging.error(f"[LocalLLMService] Failed to initialize model: {e}")
            self.is_initialized = False

    def generate_therapy_response(self, user_message, conversation_history=None, personality=None, user_id=None, emotion_probs=None):
        """Generate therapy response with fallback to rule-based responses"""
        if not self.is_initialized or not self.tokenizer or not self.model:
            logging.warning("[LocalLLMService] Model not initialized, using fallback responses")
            return self.generate_fallback_response(user_message, personality), "concerned"
        
        try:
            # Log emotion detector output
            logging.info(f"[LocalLLMService] Emotion detector output: {emotion_probs}")
            print(f"[LocalLLMService] Emotion detector output: {emotion_probs}")
            prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>\nYou are a Psychology Assistant, designed to answer users' questions in a kind, empathetic, and respectful manner, drawing from psychological principles and research to provide thoughtful support.DO NOT USE THE NAME OF THE PERSON IN YOUR RESPONSE"""
            if emotion_probs:
                prompt += f"\nThe user's current facial emotion probabilities are: {emotion_probs}"  # Add emotion_probs to the prompt
            prompt += f"<|eot_id|><|start_header_id|>user<|end_header_id|>\n{user_message}<|eot_id|><|start_header_id|>assistant<|end_header_id|>"
            # Log the prompt being sent to the model
            logging.info(f"[LocalLLMService] Prompt sent to model:\n{prompt}")
            print(f"[LocalLLMService] Prompt sent to model:\n{prompt}")
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=1024,  # Increased for longer responses
                    do_sample=True,
                    temperature=0.7,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            full_output = self.tokenizer.decode(outputs[0], skip_special_tokens=False)
            logging.info(f"[LocalLLMService] Model output:\n{full_output}")
            assistant_response = full_output.split("<|end_header_id|>")[-1].strip()
            # Remove special tokens
            for token in ["<|eot_id|>", "<|end_header_id|>", "<|begin_of_text|>", "<|start_header_id|>"]:
                assistant_response = assistant_response.replace(token, "")
            assistant_response = assistant_response.strip()
            return assistant_response, "speaking"
        except Exception as e:
            logging.error(f"[LocalLLMService] Error generating response: {e}")
            return self.generate_fallback_response(user_message, personality), "concerned"
    
    def generate_fallback_response(self, user_message, personality="warm"):
        """Generate fallback responses when model is not available"""
        message = user_message.lower()
        
        # Crisis detection
        crisis_keywords = ['kill myself', 'suicide', 'want to die', 'end it all', 'no reason to live']
        if any(keyword in message for keyword in crisis_keywords):
            return "I'm very concerned about what you're sharing. Your life has value, and there are people who care about you. Please reach out to a crisis helpline immediately - you can call 988 (Suicide & Crisis Lifeline) or 911. You don't have to face this alone."
        
        # Emotion detection
        emotions = {
            'sad': ['sad', 'depressed', 'down', 'upset', 'cry', 'hurt', 'pain'],
            'anxious': ['anxious', 'worry', 'nervous', 'stress', 'panic', 'afraid', 'scared'],
            'angry': ['angry', 'mad', 'furious', 'frustrated', 'annoyed', 'rage'],
            'happy': ['happy', 'good', 'great', 'excited', 'joy', 'wonderful', 'amazing'],
            'confused': ['confused', 'lost', 'don\'t know', 'unsure', 'unclear']
        }
        
        detected_emotion = 'neutral'
        for emotion, keywords in emotions.items():
            if any(keyword in message for keyword in keywords):
                detected_emotion = emotion
                break
        
        # Personality-based responses
        responses = {
            'warm': {
                'sad': "I can hear the pain in your words, and I want you to know that your feelings are completely valid. What do you think might help you feel a little lighter today?",
                'anxious': "It sounds like anxiety is really weighing on you right now. Let's take a moment to breathe together. What specific thoughts are making you feel most worried?",
                'angry': "Your anger makes complete sense given what you're dealing with. It's actually a sign that something important to you has been affected. What do you think is at the core of these feelings?",
                'happy': "I love hearing the joy in your words! It's wonderful that you're experiencing happiness. What's contributing most to these positive feelings?",
                'confused': "Feeling uncertain can be really uncomfortable, but it often means you're on the verge of important growth. What aspects of the situation feel clearest to you?",
                'neutral': "I'm here to listen to whatever you'd like to share. What's been on your mind lately?"
            }
        }
        
        personality_responses = responses.get(personality, responses['warm'])
        return personality_responses.get(detected_emotion, personality_responses['neutral'])

# Initialize service
local_llm_service = LocalLLMService(settings.local_llm_model_id) 