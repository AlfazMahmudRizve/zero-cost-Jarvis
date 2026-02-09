"""
LLM Integration Module (The Brain)
Handles communication with Ollama (local) or Google Gemini (cloud).
"""

import asyncio
from typing import List, Dict, Optional
from src.core.config import settings
from src.core.logger import get_logger, error_message
from src.brain.prompts import SHERIFF_SYSTEM_PROMPT

logger = get_logger(__name__)


class Brain:
    """
    The Intelligence Unit.
    Manages LLM sessions, context, and decision making.
    Supports: Ollama (local), Gemini (cloud)
    """

    def __init__(self):
        self.provider = settings.llm_provider.lower()
        self.history: List[Dict[str, str]] = []
        self._connected = False
        
        # Initialize Memory
        from src.memory import d_hippocampus
        self.memory = d_hippocampus
        
        # Initialize based on provider
        if self.provider == "ollama":
            self._init_ollama()
        elif self.provider == "gemini":
            self._init_gemini()
        else:
            logger.warning(f"Unknown LLM provider: {self.provider}. Defaulting to Ollama.")
            self._init_ollama()

    def _init_ollama(self):
        """Initialize Ollama (local LLM)."""
        try:
            import ollama
            self.ollama_client = ollama
            self.ollama_model = settings.ollama_model
            
            # Test connection by listing models
            models = ollama.list()
            available = [m['model'] for m in models.get('models', [])]
            
            if self.ollama_model not in available and f"{self.ollama_model}:latest" not in available:
                logger.warning(f"Model '{self.ollama_model}' not found. Available: {available}")
                logger.info(f"Attempting to pull {self.ollama_model}...")
                # Note: Pull requires Ollama server running
            
            self._connected = True
            logger.info(f"Brain initialized with Ollama (model: {self.ollama_model})")
            
        except ImportError:
            logger.error("Ollama package not installed. Run: pip install ollama")
            self._connected = False
        except Exception as e:
            logger.error(f"Failed to connect to Ollama: {e}")
            logger.error("Make sure Ollama is running: https://ollama.ai")
            self._connected = False

    def _init_gemini(self):
        """Initialize Google Gemini (cloud LLM)."""
        try:
            import google.generativeai as genai
            
            api_key = settings.gemini_api_key
            if not api_key:
                logger.warning("Gemini API Key missing. Brain will be offline.")
                return

            genai.configure(api_key=api_key)
            
            self.gemini_model = genai.GenerativeModel(
                model_name=settings.gemini_model,
                system_instruction=SHERIFF_SYSTEM_PROMPT
            )
            
            self._chat_session = self.gemini_model.start_chat(history=[])
            self._connected = True
            logger.info(f"Brain initialized with Gemini (model: {settings.gemini_model})")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")
            logger.error("Check if your API key is valid at https://aistudio.google.com/apikey")
            self._connected = False

    async def think(self, text: str, image_path: str = None) -> str:
        """
        Process input text through the LLM.
        """
        if not self._connected:
            return "Offline Mode: Brain not connected. Check Ollama or Gemini configuration."

        try:
            logger.info(f"Brain thinking... Input: '{text}'")
            
            # 1. Recall Memory
            context = self.memory.recall(text)
            
            # 2. Construct Prompt with Context
            full_prompt = text
            if context:
                full_prompt = f"{context}\n\nUser Query: {text}"
                logger.debug("Injected memory context into prompt")

            # 3. Send to LLM (based on provider)
            if self.provider == "ollama":
                response_text = await self._think_ollama(full_prompt)
            else:
                response_text = await self._think_gemini(full_prompt)
            
            # 4. Memorize Interaction
            self.memory.memorize(text, "user")
            self.memory.memorize(response_text, "sheriff")
            
            logger.info(f"Brain output: '{response_text[:50]}...'")
            return response_text

        except Exception as e:
            logger.error(f"Brain error: {e}", exc_info=True)
            return "I am encountering cognitive network errors, Sir."

    async def _think_ollama(self, prompt: str) -> str:
        """Send prompt to Ollama and return response."""
        loop = asyncio.get_running_loop()
        
        # Ollama chat is blocking, so run in executor
        def _call_ollama():
            messages = [
                {"role": "system", "content": SHERIFF_SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ]
            response = self.ollama_client.chat(
                model=self.ollama_model,
                messages=messages
            )
            return response['message']['content']
        
        return await loop.run_in_executor(None, _call_ollama)

    async def _think_gemini(self, prompt: str) -> str:
        """Send prompt to Gemini and return response."""
        loop = asyncio.get_running_loop()
        
        response = await loop.run_in_executor(
            None, 
            self._chat_session.send_message, 
            prompt
        )
        
        return response.text.strip()


# Singleton instance
d_brain = Brain()
