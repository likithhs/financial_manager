import os
import json
from config import Config

class AIService:
    """
    Modular AI service wrapper.
    If an external AI API key (e.g. Gemini, OpenAI) is configured in .env,
    it can connect to the API. If not configured, it gracefully defaults
    to the built-in intelligent rule-based local assistant.
    """
    @staticmethod
    def is_api_configured():
        return bool(Config.AI_API_KEY and Config.AI_API_KEY.strip())

    @staticmethod
    def call_external_llm(system_prompt, user_message, context_dict):
        """
        Optional external LLM API client.
        Academic-ready design: returns None if API is not active so local rule-based engine handles it.
        """
        if not AIService.is_api_configured():
            return None
        
        # Example interface for external API (kept plug-and-play)
        try:
            # Here an API call to Gemini/OpenAI could be made using requests
            # For local BCA demonstration, returns None to prioritize deterministic rule-based engine
            return None
        except Exception as e:
            print(f"External AI API Error: {e}")
            return None
