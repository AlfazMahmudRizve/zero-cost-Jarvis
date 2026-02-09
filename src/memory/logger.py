"""
Memory Logger (The Cortex)
Simple file-based persistence for JARVIS context.
"""

import os
import datetime
from typing import List

MEMORY_FILE = os.path.join(os.getcwd(), "logs", "sheriff_memory.log")

def _ensure_log_dir():
    os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)

def log_interaction(user_input: str, jarvis_response: str):
    """Logs an interaction pair to the persistent memory file."""
    _ensure_log_dir()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] USER: {user_input} | JARVIS: {jarvis_response}\n"
    
    try:
        with open(MEMORY_FILE, "a", encoding="utf-8") as f:
            f.write(entry)
    except Exception as e:
        print(f"Memory Log Error: {e}")

def read_recent_context(limit: int = 5) -> str:
    """Reads the last N interactions from memory."""
    if not os.path.exists(MEMORY_FILE):
        return ""
        
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
            # Get last limit lines
            recent = lines[-limit:]
            return "".join(recent)
    except Exception:
        return ""
