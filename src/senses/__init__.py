"""
Senses Module - Complete Audio Pipeline
"""

from .audio import AudioInput
from .stt import STTEngine
from .tts import TTSEngine

d_mic = AudioInput()
d_stt = STTEngine()
d_tts = TTSEngine()

__all__ = ["d_mic", "d_stt", "d_tts", "AudioInput", "STTEngine", "TTSEngine"]
