"""
JARVIS Custom Exceptions
Hierarchical exception system for clean error handling.
"""


class JarvisError(Exception):
    """Base exception for all JARVIS errors."""
    
    def __init__(self, message: str, details: str | None = None) -> None:
        self.message = message
        self.details = details
        super().__init__(self.message)
    
    def __str__(self) -> str:
        if self.details:
            return f"{self.message} | Details: {self.details}"
        return self.message


# ═══════════════════════════════════════════════════════════════
# CONFIGURATION ERRORS
# ═══════════════════════════════════════════════════════════════

class ConfigurationError(JarvisError):
    """Raised when there's a configuration problem."""
    pass


class MissingAPIKeyError(ConfigurationError):
    """Raised when a required API key is missing."""
    
    def __init__(self, provider: str) -> None:
        super().__init__(
            f"Missing API key for {provider}",
            f"Please set the {provider.upper()}_API_KEY in your .env file"
        )


# ═══════════════════════════════════════════════════════════════
# LLM ERRORS
# ═══════════════════════════════════════════════════════════════

class LLMError(JarvisError):
    """Base exception for LLM-related errors."""
    pass


class LLMConnectionError(LLMError):
    """Raised when unable to connect to LLM provider."""
    pass


class LLMResponseError(LLMError):
    """Raised when LLM returns an invalid response."""
    pass


class LLMRateLimitError(LLMError):
    """Raised when hitting rate limits."""
    pass


# ═══════════════════════════════════════════════════════════════
# AUDIO ERRORS
# ═══════════════════════════════════════════════════════════════

class AudioError(JarvisError):
    """Base exception for audio-related errors."""
    pass


class MicrophoneError(AudioError):
    """Raised when there's an issue with the microphone."""
    pass


class STTError(AudioError):
    """Raised when speech-to-text fails."""
    pass


class TTSError(AudioError):
    """Raised when text-to-speech fails."""
    pass


# ═══════════════════════════════════════════════════════════════
# MEMORY ERRORS
# ═══════════════════════════════════════════════════════════════

class MemoryError(JarvisError):
    """Base exception for memory/vector store errors."""
    pass


class MemoryStoreError(MemoryError):
    """Raised when storing to memory fails."""
    pass


class MemoryRetrievalError(MemoryError):
    """Raised when retrieving from memory fails."""
    pass


# ═══════════════════════════════════════════════════════════════
# VISION ERRORS
# ═══════════════════════════════════════════════════════════════

class VisionError(JarvisError):
    """Base exception for vision-related errors."""
    pass


class CameraError(VisionError):
    """Raised when camera access fails."""
    pass


class ScreenCaptureError(VisionError):
    """Raised when screen capture fails."""
    pass


# ═══════════════════════════════════════════════════════════════
# TOOL ERRORS
# ═══════════════════════════════════════════════════════════════

class ToolError(JarvisError):
    """Base exception for tool execution errors."""
    pass


class ToolExecutionError(ToolError):
    """Raised when a tool fails to execute."""
    
    def __init__(self, tool_name: str, reason: str) -> None:
        super().__init__(
            f"Tool '{tool_name}' failed to execute",
            reason
        )


class ToolNotFoundError(ToolError):
    """Raised when a requested tool doesn't exist."""
    
    def __init__(self, tool_name: str) -> None:
        super().__init__(f"Tool '{tool_name}' not found")
