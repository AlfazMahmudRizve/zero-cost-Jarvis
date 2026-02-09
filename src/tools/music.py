"""
Music Tool (The DJ)
Uses yt-dlp and mpv to stream music without a browser.
"""

import subprocess
import os
import signal
from src.core.logger import get_logger

logger = get_logger(__name__)

# Track the current music process
_music_process = None

def play_music(song_name: str) -> str:
    """
    Streams music from YouTube using yt-dlp and mpv.
    Args:
        song_name: The name of the song/query to search.
    Returns:
        Status message.
    """
    global _music_process
    
    # constant cleanup
    stop_music()
    
    logger.info(f"DJ: Searching for '{song_name}'...")
    
    # Command: mpv ytdl://ytsearch1:query --no-video
    # Ensure yt-dlp is in PATH for mpv to find it
    import sys
    
    # Add .venv/Scripts to PATH for this process
    current_env = os.environ.copy()
    venv_scripts = os.path.join(os.getcwd(), ".venv", "Scripts")
    if venv_scripts not in current_env["PATH"]:
        current_env["PATH"] = venv_scripts + os.pathsep + current_env["PATH"]
    
    mpv_cmd = [
        "mpv",
        f"ytdl://ytsearch1:{song_name}",
        "--no-video",
        "--no-terminal"
    ]
    
    try:
        # Start mpv directly
        _music_process = subprocess.Popen(
            mpv_cmd, 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL,
            shell=False,
            env=current_env
        )
        
        return f"Streaming '{song_name}' in the background, Sheriff."
        
        return f"Streaming '{song_name}' in the background, Sheriff."
        
    except FileNotFoundError:
        return "Error: MPV or yt-dlp not found. Please install them (winget install mpv)."
    except Exception as e:
        logger.error(f"Music Error: {e}")
        return f"Failed to play music: {e}"

def stop_music() -> str:
    """Stops the currently playing music."""
    global _music_process
    
    # Use taskkill to be sure (windows specific)
    try:
        subprocess.run(["taskkill", "/IM", "mpv.exe", "/F"], 
                      stdout=subprocess.DEVNULL, 
                      stderr=subprocess.DEVNULL,
                      check=False)
        _music_process = None
        return "Music stopped, Sheriff."
    except Exception as e:
        return f"Error stopping music: {e}"

def is_music_playing() -> bool:
    """Checks if music is currently playing."""
    global _music_process
    if _music_process and _music_process.poll() is None:
        return True
    return False
