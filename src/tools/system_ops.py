"""
System Ops (The Hands)
PowerShell control and Focus Mode management.
"""

import subprocess
from src.core.logger import get_logger

logger = get_logger(__name__)

DISTRACTIONS = ["steam.exe", "discord.exe", "epicgameslauncher.exe", "spotify.exe"]
STARTUP_APPS = []  # Add apps to launch on focus exit if needed

def execute_powershell(script: str) -> str:
    """
    Executes a raw PowerShell script/command.
    """
    try:
        # -NoProfile -ExecutionPolicy Bypass -Command ...
        cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script]
        
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=30
        )
        
        if result.returncode == 0:
            return f"Success:\n{result.stdout[:500]}"
        else:
            return f"Error:\n{result.stderr[:500]}"
            
    except Exception as e:
        return f"PowerShell Execution Failed: {str(e)}"

def toggle_focus_mode(state: bool) -> str:
    """
    True: Kills distractions.
    False: Launches startup apps (optional).
    """
    if state:
        logger.info("Engaging Focus Mode...")
        killed_count = 0
        for app in DISTRACTIONS:
            # taskkill /IM app /F
            res = subprocess.run(
                ["taskkill", "/IM", app, "/F"], 
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.DEVNULL
            )
            if res.returncode == 0:
                killed_count += 1
                
        return f"Focus Mode ON. Eliminated {killed_count} distractions."
    else:
        return "Focus Mode OFF. You are free to roam, Sheriff."
