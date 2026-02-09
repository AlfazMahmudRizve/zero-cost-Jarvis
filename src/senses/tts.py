"""
Text-to-Speech (TTS) Module with Interruption Support
Uses edge-tts for synthesis and pygame for playback.
"""

import asyncio
import time
import os
import pygame
import edge_tts
import subprocess
from pathlib import Path
from src.core.config import settings
from src.core.logger import get_logger

logger = get_logger(__name__)


class TTSEngine:
    """TTS Engine with interruption support."""

    def __init__(self):
        self.voice = settings.tts_voice
        self.rate = settings.tts_rate
        self.temp_dir = Path(".audio_cache")
        self.temp_dir.mkdir(exist_ok=True)
        
        self._is_speaking = False
        self._process = None
        
        logger.info("TTS Engine initialized (MPV Mode)")

    @property
    def is_speaking(self) -> bool:
        return self._is_speaking

    def stop(self):
        """Immediately silence audio using taskkill."""
        if self._process:
            try:
                self._process.terminate()
            except:
                pass
            self._process = None
        
        # Force kill any mpv instances
        try:
            os.system("taskkill /F /IM mpv.exe >nul 2>&1")
        except:
            pass
            
        self._is_speaking = False
        logger.info("TTS Stopped (Barge-In sequence)")

    async def speak(self, text: str) -> None:
        """Synthesize and speak text using MPV."""
        if not text or len(text.strip()) < 2:
            return

        # Stop previous
        self.stop()
        
        self._is_speaking = True
        logger.info(f"TTS: '{text[:50]}...'")
        
        try:
            # Generate unique filename
            self._file_counter = getattr(self, "_file_counter", 0) + 1
            output_file = self.temp_dir / f"speech_{self._file_counter}.mp3"
            
            # Clean up old file if exists
            if output_file.exists():
                try:
                    output_file.unlink()
                except Exception:
                    pass

            # Generate audio using edge-tts
            communicate = edge_tts.Communicate(text, self.voice, rate=self.rate)
            await communicate.save(str(output_file))
            
            # Use MPV to play
            # --no-terminal: quiet
            self._process = subprocess.Popen(
                ["mpv", "--no-terminal", "--volume=100", str(output_file)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # Wait for completion but allow interruption
            while self._process and self._process.poll() is None:
                await asyncio.sleep(0.1)
            
        except Exception as e:
            logger.error(f"TTS error: {e}")
        finally:
            self._is_speaking = False
            self._process = None

    def _cleanup(self):
        pass # Minimal cleanup needed as we overwrite or use temp dir logic elsewhere

# Singleton
d_tts = TTSEngine()
