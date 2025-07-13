import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from core.config import get_settings
import logging

settings = get_settings()

class LocalLLMService:
    def __init__(self, model_id):
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
        )
        self.model.to("cuda" if torch.cuda.is_available() else "cpu")

    def generate_therapy_response(self, user_message, conversation_history=None, personality=None, user_id=None):
        prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>\nYou are a Psychology Assistant, designed to answer users' questions in a kind, empathetic, and respectful manner, drawing from psychological principles and research to provide thoughtful support.DO NOT USE THE NAME OF THE PERSON IN YOUR RESPONSE<|eot_id|><|start_header_id|>user<|end_header_id|>\n{user_message}<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""
        logging.info(f"[LocalLLMService] Prompt sent to model:\n{prompt}")
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=200,
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

local_llm_service = LocalLLMService(settings.local_llm_model_id) 