"""
Text-to-Speech (TTS) Module with Interruption Support
Uses edge-tts for synthesis and pygame for playback.
"""

import asyncio
import time
import os
import pygame
import edge_tts
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
        self._interrupt_requested = False
        self._file_counter = 0
        
        # Initialize pygame mixer
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        except Exception:
            pygame.mixer.init()
        logger.info("TTS Engine initialized")

    @property
    def is_speaking(self) -> bool:
        return self._is_speaking

    def interrupt(self):
        """Request interruption of current speech."""
        if self._is_speaking:
            self._interrupt_requested = True
            try:
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()
            except Exception:
                pass
            logger.info("TTS interrupted")

    async def speak(self, text: str) -> None:
        """Synthesize and speak text."""
        if not text or len(text.strip()) < 2:
            return

        self._interrupt_requested = False
        self._is_speaking = True
        
        logger.info(f"TTS: '{text[:50]}...'")
        
        try:
            # Generate unique filename
            self._file_counter += 1
            output_file = self.temp_dir / f"speech_{self._file_counter}.mp3"
            
            # Clean up old file if exists
            if output_file.exists():
                try:
                    output_file.unlink()
                except Exception:
                    output_file = self.temp_dir / f"speech_{int(time.time())}.mp3"

            # Generate audio using edge-tts
            communicate = edge_tts.Communicate(text, self.voice, rate=self.rate)
            await communicate.save(str(output_file))
            
            # Wait for file to be written completely
            await asyncio.sleep(0.1)
            
            # Verify file exists and has content
            if not output_file.exists() or output_file.stat().st_size < 100:
                logger.error("TTS file generation failed")
                return
            
            # Play audio
            await self._play_audio(str(output_file))
            
            # Cleanup old files
            self._cleanup()
            
        except Exception as e:
            logger.error(f"TTS error: {e}")
        finally:
            self._is_speaking = False

    async def _play_audio(self, file_path: str):
        """Play audio file with interruption support."""
        try:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy():
                if self._interrupt_requested:
                    pygame.mixer.music.stop()
                    break
                await asyncio.sleep(0.05)
            
            pygame.mixer.music.unload()
                
        except Exception as e:
            logger.error(f"Playback error: {e}")

    def _cleanup(self):
        """Remove old audio files."""
        try:
            files = sorted(self.temp_dir.glob("speech_*.mp3"), key=lambda f: f.stat().st_mtime)
            for f in files[:-3]:
                try:
                    f.unlink()
                except Exception:
                    pass
        except Exception:
            pass


# Singleton
d_tts = TTSEngine()
