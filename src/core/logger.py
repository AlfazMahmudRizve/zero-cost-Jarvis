"""
JARVIS Logging System
Rich console output with file logging for debugging.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.logging import RichHandler
from rich.theme import Theme

# ═══════════════════════════════════════════════════════════════
# CUSTOM THEME FOR JARVIS
# ═══════════════════════════════════════════════════════════════
JARVIS_THEME = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "red bold",
    "critical": "red bold reverse",
    "success": "green bold",
    "jarvis": "blue bold",
    "user": "magenta",
    "system": "dim white",
})

# Global console instance
console = Console(theme=JARVIS_THEME)

# Logger cache
_loggers: dict[str, logging.Logger] = {}


class JarvisFormatter(logging.Formatter):
    """Custom formatter with colored level names for file output."""
    
    LEVEL_COLORS = {
        "DEBUG": "\033[36m",     # Cyan
        "INFO": "\033[32m",      # Green
        "WARNING": "\033[33m",   # Yellow
        "ERROR": "\033[31m",     # Red
        "CRITICAL": "\033[41m",  # Red background
    }
    RESET = "\033[0m"
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with timestamp and level."""
        log_message = super().format(record)
        return log_message


def setup_logging(
    level: str = "INFO",
    log_file: Optional[Path] = None,
    enable_file_logging: bool = True,
) -> None:
    """
    Configure the logging system for JARVIS.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file. If None, uses default from settings.
        enable_file_logging: Whether to enable file logging.
    """
    from .config import settings
    
    # Ensure log directory exists
    settings.ensure_directories()
    
    log_file = log_file or settings.log_file
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # ─────────────────────────────────────────────────────────────
    # Console Handler (Rich)
    # ─────────────────────────────────────────────────────────────
    console_handler = RichHandler(
        console=console,
        show_time=True,
        show_path=False,
        rich_tracebacks=True,
        tracebacks_show_locals=True,
        markup=True,
    )
    console_handler.setLevel(log_level)
    console_handler.setFormatter(logging.Formatter("%(message)s"))
    root_logger.addHandler(console_handler)
    
    # ─────────────────────────────────────────────────────────────
    # File Handler
    # ─────────────────────────────────────────────────────────────
    if enable_file_logging and log_file:
        file_handler = logging.FileHandler(
            log_file,
            mode="a",
            encoding="utf-8",
        )
        file_handler.setLevel(logging.DEBUG)  # Always capture everything to file
        file_formatter = JarvisFormatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
    
    # Suppress noisy third-party loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the given name.
    
    Args:
        name: Logger name (typically __name__ of the calling module)
        
    Returns:
        Configured logger instance
    """
    if name not in _loggers:
        _loggers[name] = logging.getLogger(name)
    return _loggers[name]


# ═══════════════════════════════════════════════════════════════
# JARVIS-SPECIFIC OUTPUT FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def jarvis_speak(message: str) -> None:
    """Print a message as JARVIS speaking."""
    console.print(f"[jarvis]🤖 JARVIS:[/jarvis] {message}")


def user_speak(message: str) -> None:
    """Print a message as the user speaking."""
    console.print(f"[user]👤 USER:[/user] {message}")


def system_message(message: str) -> None:
    """Print a system status message."""
    console.print(f"[system]⚙️  {message}[/system]")


def success_message(message: str) -> None:
    """Print a success message."""
    console.print(f"[success]✅ {message}[/success]")


def error_message(message: str) -> None:
    """Print an error message."""
    console.print(f"[error]❌ {message}[/error]")


def warning_message(message: str) -> None:
    """Print a warning message."""
    console.print(f"[warning]⚠️  {message}[/warning]")
