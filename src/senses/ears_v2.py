"""
Natural Ears (Ears V2)
Advanced audio input pipeline with Silero VAD and conversational latching.
"""

import torch
import numpy as np
import sounddevice as sd
import time
import asyncio
from typing import Tuple, Optional

from src.core.config import settings
from src.core.logger import get_logger, console

logger = get_logger(__name__)

class NaturalEars:
    def __init__(self):
        logger.info("Initializing NaturalEars (Silero VAD)...")
        try:
            # Load Silero VAD
            self.model, utils = torch.hub.load(
                repo_or_dir='snakers4/silero-vad',
                model='silero_vad',
                force_reload=False,
                trust_repo=True
            )
            (self.get_speech_timestamps, self.save_audio, self.read_audio, self.VADIterator, self.collect_chunks) = utils
            self.model.eval() # Set to evaluation mode
            self.vad_iterator = self.VADIterator(self.model)
            logger.info("Silero VAD loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load Silero VAD: {e}")
            raise

        # Audio Config
        self.sample_rate = 16000 # Silero works best at 16k
        self.block_size = 512    # Chunk size for VAD
        
        # Latch State
        self.latch_active = False
        self.latch_timeout = 8.0 # Seconds
        self.latch_end_time = 0.0

    def activate_latch(self):
        """Activate conversational mode (bypass wake word)."""
        self.latch_active = True
        self.latch_end_time = time.time() + self.latch_timeout
        logger.debug(f"Latch activated for {self.latch_timeout}s")

    def check_latch(self) -> bool:
        """Check if latch is still valid."""
        if not self.latch_active:
            return False
            
        if time.time() > self.latch_end_time:
            self.latch_active = False
            logger.debug("Latch expired.")
            return False
            
        return True

    def is_human_speech(self, audio_chunk: np.ndarray) -> bool:
        """
        Check if chunk contains speech using Silero.
        Expects float32 array [-1, 1].
        """
        # Silero expects tensor
        with torch.no_grad():
            tensor = torch.from_numpy(audio_chunk)
            speech_prob = self.model(tensor, self.sample_rate).item()
            
        return speech_prob > 0.6 # Confidence threshold

    def clean_audio(self, audio_chunk: np.ndarray) -> np.ndarray:
        """Placeholder for audio implementation."""
        # TODO: Implement DeepFilterNet or simple bandpass
        return audio_chunk

    async def listen(self) -> np.ndarray:
        """
        Listens for a complete phrase.
        Returns float32 numpy array of audio.
        Blocks until speech starts and ends.
        """
        buffer = []
        is_speaking = False
        silence_counter = 0
        silence_threshold = 20 # blocks (~0.6s)
        
        logger.debug("Listening for speech...")
        
        try:
            # Use InputStream context manager for continuous reading
            with sd.InputStream(samplerate=self.sample_rate, channels=1, blocksize=self.block_size) as stream:
                while True:
                    # Read block (blocking call efficiently handled by sounddevice)
                    # Note: stream.read returns (data, overflowed)
                    chunk, overflowed = stream.read(self.block_size)
                    
                    if overflowed:
                        logger.warning("Audio buffer overflow")
                        
                    chunk = chunk.squeeze() # Remove channel dim
                    
                    # Check VAD
                    if self.is_human_speech(chunk):
                        if not is_speaking:
                            # Speech started
                            is_speaking = True
                            buffer.append(chunk) # Include start
                        else:
                            buffer.append(chunk)
                        silence_counter = 0
                    else:
                        if is_speaking:
                            buffer.append(chunk) # Include tail
                            silence_counter += 1
                            if silence_counter > silence_threshold:
                                # Speech ended
                                break
                        else:
                            # Not speaking yet, just noise
                            pass

                    # Yield to event loop occasionally to keep UI responsive
                    await asyncio.sleep(0.01) 
                    
                    # Check Latch expiration periodically
                    if self.check_latch():
                        pass

        except Exception as e:
            logger.error(f"Error reading audio stream: {e}")
            return np.array([], dtype=np.float32)

        # Combine buffer
        if not buffer:
             return np.array([], dtype=np.float32)
             
        full_audio = np.concatenate(buffer)
        
        # Clean
        full_audio = self.clean_audio(full_audio)
        
        return full_audio
