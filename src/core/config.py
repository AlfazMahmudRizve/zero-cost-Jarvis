"""
JARVIS Configuration Management
Centralized settings using Pydantic for validation and type safety.
"""

from pathlib import Path
from typing import Literal, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    All settings have sensible defaults for zero-config startup.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ═══════════════════════════════════════════════════════════════
    # LLM BRAIN CONFIGURATION
    # ═══════════════════════════════════════════════════════════════
    gemini_api_key: Optional[str] = Field(default=None, description="Google Gemini API Key")
    groq_api_key: Optional[str] = Field(default=None, description="Groq API Key (fallback)")
    
    llm_provider: Literal["gemini", "groq", "ollama"] = Field(
        default="groq", 
        description="Primary LLM provider"
    )
    gemini_model: str = Field(
        default="gemini-1.5-flash",
        description="Gemini model to use"
    )
    groq_model: str = Field(
        default="llama-3.1-70b-versatile",
        description="Groq model to use"
    )
    ollama_model: str = Field(
        default="llama3.2",
        description="Ollama model to use"
    )
    
    # ═══════════════════════════════════════════════════════════════
    # SPEECH-TO-TEXT (STT) CONFIGURATION
    # ═══════════════════════════════════════════════════════════════
    stt_provider: Literal["local", "groq"] = Field(
        default="groq",
        description="STT provider: 'local' for faster-whisper, 'groq' for cloud"
    )
    whisper_model_size: Literal["tiny", "base", "small", "medium", "large-v2", "large-v3"] = Field(
        default="base",
        description="Whisper model size for local STT"
    )
    
    # ═══════════════════════════════════════════════════════════════
    # TEXT-TO-SPEECH (TTS) CONFIGURATION
    # ═══════════════════════════════════════════════════════════════
    tts_voice: str = Field(
        default="en-US-AriaNeural",
        description="Edge TTS voice name"
    )
    tts_rate: str = Field(
        default="+10%",
        description="TTS speech rate adjustment"
    )
    
    # ═══════════════════════════════════════════════════════════════
    # WAKE WORD CONFIGURATION
    # ═══════════════════════════════════════════════════════════════
    wake_word: str = Field(
        default="jarvis",
        description="Wake word to activate the assistant"
    )
    wake_word_sensitivity: float = Field(
        default=0.6,
        ge=0.0,
        le=1.0,
        description="Wake word detection sensitivity (0.0 - 1.0)"
    )
    
    # ═══════════════════════════════════════════════════════════════
    # MEMORY CONFIGURATION
    # ═══════════════════════════════════════════════════════════════
    chroma_persist_path: Path = Field(
        default=Path("./data/chroma_db"),
        description="Path for ChromaDB persistence"
    )
    memory_collection_name: str = Field(
        default="jarvis_memory",
        description="ChromaDB collection name"
    )
    
    # ═══════════════════════════════════════════════════════════════
    # VISION CONFIGURATION
    # ═══════════════════════════════════════════════════════════════
    enable_vision: bool = Field(
        default=False,
        description="Enable vision capabilities"
    )
    screenshot_interval: int = Field(
        default=5,
        ge=1,
        description="Seconds between automatic screenshots"
    )
    
    # ═══════════════════════════════════════════════════════════════
    # AUDIO CONFIGURATION
    # ═══════════════════════════════════════════════════════════════
    audio_sample_rate: int = Field(
        default=16000,
        description="Audio sample rate in Hz"
    )
    audio_channels: int = Field(
        default=1,
        description="Number of audio channels (1=mono, 2=stereo)"
    )
    input_device_index: Optional[int] = Field(
        default=None,
        description="Index of the audio input device"
    )
    silence_threshold: int = Field(
        default=500,
        description="RMS threshold for silence detection"
    )
    silence_duration: float = Field(
        default=1.5,
        ge=0.5,
        description="Seconds of silence before stopping recording"
    )
    
    # ═══════════════════════════════════════════════════════════════
    # LOGGING CONFIGURATION
    # ═══════════════════════════════════════════════════════════════
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging verbosity level"
    )
    log_file: Path = Field(
        default=Path("./logs/jarvis.log"),
        description="Log file path"
    )
    
    # ═══════════════════════════════════════════════════════════════
    # VALIDATORS
    # ═══════════════════════════════════════════════════════════════
    @field_validator("chroma_persist_path", "log_file", mode="before")
    @classmethod
    def ensure_path(cls, v: str | Path) -> Path:
        """Convert string paths to Path objects."""
        return Path(v) if isinstance(v, str) else v
    
    # ═══════════════════════════════════════════════════════════════
    # COMPUTED PROPERTIES
    # ═══════════════════════════════════════════════════════════════
    @property
    def has_gemini_key(self) -> bool:
        """Check if Gemini API key is configured."""
        return bool(self.gemini_api_key and self.gemini_api_key != "your_gemini_api_key_here")
    
    @property
    def has_groq_key(self) -> bool:
        """Check if Groq API key is configured."""
        return bool(self.groq_api_key and self.groq_api_key != "your_groq_api_key_here")
    
    @property
    def active_llm_provider(self) -> str:
        """Get the active LLM provider based on configuration and available keys."""
        if self.llm_provider == "gemini" and self.has_gemini_key:
            return "gemini"
        elif self.llm_provider == "groq" and self.has_groq_key:
            return "groq"
        elif self.has_gemini_key:
            return "gemini"
        elif self.has_groq_key:
            return "groq"
        return "none"
    
    def ensure_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        self.chroma_persist_path.mkdir(parents=True, exist_ok=True)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)


# Singleton instance
settings = Settings()
