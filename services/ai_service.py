import os
import json
import logging
import requests
from config import Config

logger = logging.getLogger("finai")


class AIService:
    """
    Multi-Provider AI Service for FinAI Assistant.
    Supports Google Gemini, OpenAI, and Groq Cloud with graceful
    fallback to the local rule-based financial engine.
    """

    DEFAULT_MODELS = {
        'gemini': 'gemini-2.5-flash',
        'openai': 'gpt-4o-mini',
        'groq': 'llama-3.3-70b-versatile'
    }

    @staticmethod
    def get_active_provider():
        """Returns the active AI provider key and model."""
        provider = Config.AI_PROVIDER or 'gemini'
        api_key = Config.AI_API_KEY
        
        # Check provider-specific keys if AI_API_KEY wasn't set directly
        if not api_key:
            if provider == 'gemini':
                api_key = Config.GEMINI_API_KEY
            elif provider == 'openai':
                api_key = Config.OPENAI_API_KEY
            elif provider == 'groq':
                api_key = Config.GROQ_API_KEY
                
        model = Config.AI_MODEL or AIService.DEFAULT_MODELS.get(provider, 'gemini-2.5-flash')
        return provider, api_key, model

    @staticmethod
    def is_api_configured():
        """Returns True if an external API key is present."""
        provider, api_key, _ = AIService.get_active_provider()
        return bool(api_key and api_key.strip() and provider != 'local')

    @staticmethod
    def get_provider_status():
        """Returns human-readable provider status for UI badges."""
        provider, api_key, model = AIService.get_active_provider()
        if not api_key or provider == 'local':
            return {
                "provider": "local",
                "display_name": "FinAI Local Engine",
                "model": "Rule-Based Deterministic",
                "is_active": False
            }
        
        display_names = {
            'gemini': f"Gemini {model}",
            'openai': f"OpenAI {model}",
            'groq': f"Groq {model}"
        }
        
        return {
            "provider": provider,
            "display_name": display_names.get(provider, f"{provider.capitalize()} {model}"),
            "model": model,
            "is_active": True
        }

    @staticmethod
    def generate_response(system_prompt, user_message, chat_history=None):
        """
        Executes an external LLM request using the configured provider.
        Returns the generated response string, or None if fallback is required.
        """
        if not AIService.is_api_configured():
            return None

        provider, api_key, model = AIService.get_active_provider()

        try:
            if provider == 'gemini':
                return AIService._call_gemini(api_key, model, system_prompt, user_message, chat_history)
            elif provider == 'openai':
                return AIService._call_openai(api_key, model, system_prompt, user_message, chat_history)
            elif provider == 'groq':
                return AIService._call_groq(api_key, model, system_prompt, user_message, chat_history)
            else:
                logger.warning(f"Unknown AI provider '{provider}', falling back to local engine.")
                return None
        except Exception as e:
            logger.error(f"External AI Provider ({provider}) Error: {e}")
            return None

    # -------------------------------------------------------------
    # Provider-Specific Callers (Using Zero-Dependency Requests)
    # -------------------------------------------------------------

    @staticmethod
    def _call_gemini(api_key, model, system_prompt, user_message, chat_history=None):
        """Calls Google Gemini API generateContent endpoint."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        
        headers = {
            "Content-Type": "application/json"
        }

        # Build contents structure
        contents = []
        
        # Include brief past conversation context if available (up to 4 turns)
        if chat_history and isinstance(chat_history, list):
            for turn in chat_history[-4:]:
                if turn.get('user_message'):
                    contents.append({"role": "user", "parts": [{"text": turn['user_message']}]})
                if turn.get('ai_response'):
                    contents.append({"role": "model", "parts": [{"text": turn['ai_response']}]})

        contents.append({"role": "user", "parts": [{"text": user_message}]})

        payload = {
            "contents": contents,
            "systemInstruction": {
                "parts": [{"text": system_prompt}]
            },
            "generationConfig": {
                "temperature": 0.25,
                "maxOutputTokens": 1024
            }
        }

        response = requests.post(url, headers=headers, json=payload, timeout=14)
        
        # If 404/model not found with gemini-2.5-flash, fallback to gemini-1.5-flash
        if response.status_code == 404 and model != 'gemini-1.5-flash':
            logger.info(f"Gemini model {model} not found, falling back to gemini-1.5-flash")
            fallback_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            response = requests.post(fallback_url, headers=headers, json=payload, timeout=14)

        if response.status_code == 200:
            data = response.json()
            candidates = data.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                if parts:
                    return parts[0].get("text", "").strip()
            return None
        else:
            logger.error(f"Gemini API returned status {response.status_code}: {response.text}")
            return None

    @staticmethod
    def _call_openai(api_key, model, system_prompt, user_message, chat_history=None):
        """Calls OpenAI Chat Completions API."""
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        messages = [{"role": "system", "content": system_prompt}]

        if chat_history and isinstance(chat_history, list):
            for turn in chat_history[-4:]:
                if turn.get('user_message'):
                    messages.append({"role": "user", "content": turn['user_message']})
                if turn.get('ai_response'):
                    messages.append({"role": "assistant", "content": turn['ai_response']})

        messages.append({"role": "user", "content": user_message})

        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.25,
            "max_tokens": 1024
        }

        response = requests.post(url, headers=headers, json=payload, timeout=14)
        if response.status_code == 200:
            data = response.json()
            choices = data.get("choices", [])
            if choices:
                return choices[0].get("message", {}).get("content", "").strip()
            return None
        else:
            logger.error(f"OpenAI API returned status {response.status_code}: {response.text}")
            return None

    @staticmethod
    def _call_groq(api_key, model, system_prompt, user_message, chat_history=None):
        """Calls Groq Cloud OpenAI-compatible Chat Completions API."""
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        messages = [{"role": "system", "content": system_prompt}]

        if chat_history and isinstance(chat_history, list):
            for turn in chat_history[-4:]:
                if turn.get('user_message'):
                    messages.append({"role": "user", "content": turn['user_message']})
                if turn.get('ai_response'):
                    messages.append({"role": "assistant", "content": turn['ai_response']})

        messages.append({"role": "user", "content": user_message})

        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.25,
            "max_tokens": 1024
        }

        response = requests.post(url, headers=headers, json=payload, timeout=14)
        if response.status_code == 200:
            data = response.json()
            choices = data.get("choices", [])
            if choices:
                return choices[0].get("message", {}).get("content", "").strip()
            return None
        else:
            logger.error(f"Groq API returned status {response.status_code}: {response.text}")
            return None
