"""
Speech-to-Text (STT) Module
Handles transcription using faster-whisper.
"""

import asyncio
import numpy as np
import os
from faster_whisper import WhisperModel
from src.core.config import settings
from src.core.logger import get_logger
from src.utils.async_helpers import run_async

logger = get_logger(__name__)


class STTEngine:
    """
    Manages the faster-whisper model for speech transcription.
    """

    def __init__(self):
        self.model_size = settings.whisper_model_size
        self.device = "cuda" if os.environ.get("CUDA_VISIBLE_DEVICES") else "cpu"
        self.compute_type = "float16" if self.device == "cuda" else "int8"
        self._model = None

    def _load_model(self):
        """Lazy load the Whisper model."""
        if self._model is None:
            logger.info(f"Loading Whisper model ({self.model_size}) on {self.device}...")
            # Use run_async to offload heavy loading if needed? No, must happen in executor
            self._model = WhisperModel(
                self.model_size, 
                device=self.device, 
                compute_type=self.compute_type
            )
            logger.info("Whisper model loaded.")
        return self._model

    async def transcribe(self, audio_data: np.ndarray) -> str:
        """
        Transcribe audio data to text asynchronously.
        
        Args:
            audio_data: Numpy array of audio samples (float32).
            
        Returns:
            Transcribed text.
        """
        if len(audio_data) == 0:
            return ""

        if settings.stt_provider == "groq":
            return await self._transcribe_groq(audio_data)

        # Run blocking model inference in a thread
        loop = asyncio.get_running_loop()
        text = await loop.run_in_executor(None, self._run_transcription, audio_data)
        return text.strip()

    def _run_transcription(self, audio_data: np.ndarray) -> str:
        """Blocking transcription function."""
        model = self._load_model()
        
        # English-only mode for better accuracy and speed
        segments, info = model.transcribe(
            audio_data,
            language="en",
            beam_size=5,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=1000, speech_pad_ms=400),
            initial_prompt="Jarvis, service, sheriff, harvest.",  # Helps prime for wake words
            condition_on_previous_text=False,  # Prevents hallway-cates from previous audio
        )
        
        text = " ".join([segment.text for segment in segments])
        
        # Filter out short noise/hallucinations
        if len(text.strip()) < 2:
            return ""

        if text:
            logger.info(f"STT: '{text}' (Prob: {info.language_probability:.2f})")
        
        return text

    async def _transcribe_groq(self, audio_data: np.ndarray) -> str:
        """Transcribe using Groq Cloud API (Distil-Whisper)."""
        import io
        import wave
        
        # Convert float32 -> int16
        audio_int16 = (audio_data * 32767).astype(np.int16)
        
        # Write to in-memory WAV
        buffer = io.BytesIO()
        with wave.open(buffer, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2) # 16-bit
            wf.setframerate(settings.audio_sample_rate)
            wf.writeframes(audio_int16.tobytes())
            
        buffer.name = "audio.wav"
        buffer.seek(0)
        
        loop = asyncio.get_running_loop()
        
        def _call():
            from groq import Groq
            if not settings.groq_api_key:
                logger.error("Groq API Key missing for STT")
                return ""
                
            client = Groq(api_key=settings.groq_api_key)
            
            try:
                transcription = client.audio.transcriptions.create(
                    file=(buffer.name, buffer.read()),
                    model="distil-whisper-large-v3-en",
                    prompt="Jarvis, Sheriff, Service.", # Context hints
                    response_format="json"
                )
                return transcription.text
            except Exception as e:
                logger.error(f"Groq STT Error: {e}")
                return ""
                
        text = await loop.run_in_executor(None, _call)
        if text:
            logger.info(f"Groq STT: '{text}'")
        return text.strip()


# Singleton instance
d_stt = STTEngine()
