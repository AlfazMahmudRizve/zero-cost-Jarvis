"""
Async Audio Input Module
Handles microphone stream, VAD (Voice Activity Detection), and audio capture.
"""

import asyncio
import numpy as np
import sounddevice as sd
from typing import AsyncGenerator
from src.core.config import settings
from src.core.logger import get_logger

logger = get_logger(__name__)


class AudioInput:
    """
    Manages asynchronous microphone input with VAD and silence detection.
    """

    def __init__(self):
        self._running = False
        self._queue = asyncio.Queue()
        self.sample_rate = settings.audio_sample_rate
        self.block_size = int(self.sample_rate * 0.03)  # 30ms block
        
        # VAD Parameters
        # Use config value (default 500) - see notes on float32 scaling
        self.vad_threshold = 0.01  # Adjusted for sensitivity
        self.silence_duration = settings.silence_duration
        self.channels = settings.audio_channels
        self.device_index = settings.input_device_index
        
        # Robust Device Selection
        if self.device_index is None:
            try:
                # Try to find default input device
                default_device = sd.query_devices(kind='input')
                self.device_index = default_device['index']
                logger.info(f"Using default input device: {default_device['name']} (Index: {self.device_index})")
            except Exception as e:
                logger.warning(f"Could not auto-detect default input device: {e}")
                # Fallback to 0 if all else fails, or let sounddevice decide
                self.device_index = None

        logger.info("Audio Input initialized (NumPy VAD)")

    def _audio_callback(self, indata, frames, time, status):
        """Callback for sounddevice input stream."""
        if status:
            logger.warning(f"Audio input status: {status}")
        
        # Put raw audio block into the async queue
        if self._running:
            try:
                self._queue.put_nowait(indata.copy())
            except asyncio.QueueFull:
                logger.warning("Audio input queue full, dropping frames")

    async def listen(self) -> AsyncGenerator[np.ndarray, None]:
        """
        Generator that yields audio blocks while listening.
        Stops yielding after silence duration is met.
        """
        self._running = True
        silence_start_time = None
        is_speaking = False
        
        # Configure input stream
        stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            blocksize=self.block_size,
            callback=self._audio_callback,
            dtype="float32"  # Whisper prefers float32
        )

        logger.debug("Starting audio stream...")
        with stream:
            while self._running:
                try:
                    # Get audio block from queue with timeout
                    # Timeout ensures we can check if running flag changed
                    audio_block = await asyncio.wait_for(self._queue.get(), timeout=0.1)
                except asyncio.TimeoutError:
                    continue

                # Calculate volume (RMS)
                rms = np.sqrt(np.mean(audio_block**2))
                
                # Check for speech activity
                if rms > self.vad_threshold:
                    if not is_speaking:
                        is_speaking = True
                        logger.debug("Speech detected")
                    silence_start_time = None
                    yield audio_block
                else:
                    # Silence detected
                    if is_speaking:
                        if silence_start_time is None:
                            silence_start_time = asyncio.get_event_loop().time()
                        
                        elapsed_silence = asyncio.get_event_loop().time() - silence_start_time
                        
                        if elapsed_silence > self.silence_duration:
                            logger.debug(f"Silence timeout ({self.silence_duration}s). Stopping.")
                            is_speaking = False
                            break
                        
                        # Yield silence to capture trailing audio if still within window
                        yield audio_block
                    else:
                        # Initial silence, ignore or yield specifically for wake word?
                        # For simple command loop, we can ignore initial noise floor calibration
                        pass

        self._running = False
        logger.debug("Audio stream stopped.")

    async def record_phrase(self) -> np.ndarray:
        """
        Capture a single phrase of speech.
        Returns the complete audio buffer as a numpy array.
        """
        frames = []
        async for block in self.listen():
            frames.append(block)
        
        if not frames:
            return np.array([], dtype="float32")
            
        # Concatenate and flatten to 1D array for Whisper (N, 1) -> (N,)
        audio_data = np.concatenate(frames, axis=0)
        return audio_data.flatten()

    def stop(self):
        """Stop the audio input stream."""
        self._running = False

    def clear_queue(self):
        """Clear any stale audio from the queue (after interruption)."""
        cleared = 0
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
                cleared += 1
            except asyncio.QueueEmpty:
                break
        if cleared > 0:
            logger.debug(f"Cleared {cleared} stale audio chunks from queue")


# Singleton instance
d_mic = AudioInput()
