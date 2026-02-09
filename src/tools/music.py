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
    
    # Command: python -m yt_dlp options | mpv options -
    # Using sys.executable ensures we use the installed module in current env
    import sys
    yt_cmd = [
        sys.executable, "-m", "yt_dlp",
        "-f", "140",
        "-o", "-",
        f"ytsearch1:{song_name}",
        "--quiet",
        "--no-warnings"
    ]
    
    # mpv options
    # - : read from stdin
    # --no-video: audio only
    mpv_cmd = [
        "mpv",
        "-",
        "--no-video",
        "--no-terminal" 
    ]
    
    try:
        # Pipe yt-dlp -> mpv
        yt_process = subprocess.Popen(yt_cmd, stdout=subprocess.PIPE, shell=True) # shell=True for windows path search
        
        # Start mpv reading from yt_process.stdout
        # We store mpv process reference to kill it later
        _music_process = subprocess.Popen(
            mpv_cmd, 
            stdin=yt_process.stdout, 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL,
            shell=True
        )
        
        # Allow yt_process to receive SIGPIPE if mpv exits
        yt_process.stdout.close()
        
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
        subprocess.run(["taskkill", "/IM", "yt-dlp.exe", "/F"], 
                      stdout=subprocess.DEVNULL, 
                      stderr=subprocess.DEVNULL,
                      check=False)
        _music_process = None
        return "Music stopped, Sheriff."
    except Exception as e:
        return f"Error stopping music: {e}"
