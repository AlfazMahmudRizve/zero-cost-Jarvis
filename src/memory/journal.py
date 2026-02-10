"""
The Secretary (Journal Module)
Handles structured daily logging for the "Digital Exhaust".
File: src/memory/journal.py
"""

import os
import datetime
from pathlib import Path
from src.core.logger import get_logger

logger = get_logger(__name__)

# Base directory for logs
LOG_DIR = Path(__file__).parent.parent.parent / "logs"

def _ensure_log_dir():
    """Ensure the logs directory exists."""
    if not LOG_DIR.exists():
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created log directory at {LOG_DIR}")

def get_today_file() -> Path:
    """Get the path to today's log file."""
    _ensure_log_dir()
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    return LOG_DIR / f"{today}.md"

def log(category: str, message: str) -> str:
    """
    Append a log entry to today's file.
    Args:
        category: The source (User, System, Git, etc.)
        message: The content to log.
    Returns:
        Status message.
    """
    try:
        log_file = get_today_file()
        timestamp = datetime.datetime.now().strftime("%I:%M %p")
        
        # Check if new file, add header
        is_new = not log_file.exists()
        
        with open(log_file, "a", encoding="utf-8") as f:
            if is_new:
                f.write(f"# Daily Log: {datetime.datetime.now().strftime('%Y-%m-%d')}\n\n")
                f.write(f"## {timestamp} - Sheriff Online\n")
            
            # Format: - [Category] Message
            f.write(f"- [{category.upper()}] {message}\n")
            
        logger.info(f"Journaled: [{category}] {message}")
        return f"Logged to {log_file.name}."
        
    except Exception as e:
        logger.error(f"Failed to log to journal: {e}")
        return f"Error logging: {e}"

def read_log(date_str: str = "today") -> str:
    """
    Read the log for a specific date.
    Args:
        date_str: "today", "yesterday", or "YYYY-MM-DD"
    """
    try:
        if date_str == "today":
            target_date = datetime.datetime.now()
        elif date_str == "yesterday":
            target_date = datetime.datetime.now() - datetime.timedelta(days=1)
        else:
            try:
                target_date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                return "Invalid date format. Use YYYY-MM-DD."
        
        filename = target_date.strftime("%Y-%m-%d") + ".md"
        file_path = LOG_DIR / filename
        
        if not file_path.exists():
            return f"No log found for {filename}."
            
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
            
    except Exception as e:
        return f"Error reading log: {e}"
