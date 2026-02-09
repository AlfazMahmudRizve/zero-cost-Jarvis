"""
Hands Module - Full System Control
Uses PowerShell for reliable app launching.
"""

import os
import json
import webbrowser
import pyautogui
import subprocess
from typing import Dict, Any
from src.core.logger import get_logger

logger = get_logger(__name__)

# Common apps and their Windows process names
COMMON_APPS = {
    # Browsers
    "chrome": "chrome", "google chrome": "chrome",
    "firefox": "firefox", "edge": "msedge", "brave": "brave",
    # Microsoft Office
    "word": "winword", "excel": "excel", "powerpoint": "powerpnt",
    "outlook": "outlook", "onenote": "onenote",
    # Development
    "vscode": "code", "visual studio code": "code", "vs code": "code",
    "notepad": "notepad", "notepad++": "notepad++",
    "terminal": "wt", "windows terminal": "wt",
    "cmd": "cmd", "powershell": "powershell",
    # System
    "explorer": "explorer", "file explorer": "explorer",
    "task manager": "taskmgr", "control panel": "control",
    "calculator": "calc", "paint": "mspaint",
    # Media
    "spotify": "spotify", "vlc": "vlc",
    # Communication
    "discord": "discord", "slack": "slack", "teams": "msteams",
    "zoom": "zoom", "telegram": "telegram", "whatsapp": "whatsapp",
    # Other
    "steam": "steam", "obs": "obs64",
}


class Hands:
    """PC Automation using PowerShell for reliability."""

    def __init__(self):
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1
        logger.info("Hands initialized")

    async def execute_action(self, json_string: str) -> str:
        """Parse and execute a JSON action."""
        try:
            # Clean JSON
            clean_json = json_string.strip()
            if "```" in clean_json:
                for part in clean_json.split("```"):
                    if "{" in part and "}" in part:
                        clean_json = part.replace("json", "").strip()
                        break
            
            start = clean_json.find("{")
            end = clean_json.rfind("}") + 1
            if start != -1 and end > start:
                clean_json = clean_json[start:end]
            
            command = json.loads(clean_json)
            
            tool = command.get("tool", "").lower()
            action = command.get("action", "").lower()
            value = command.get("value", "")
            
            logger.info(f"Executing: {tool} -> {action} ({value})")
            
            if tool == "browser":
                return self._browser(action, value)
            elif tool == "media":
                return self._media(action, value)
            elif tool == "system":
                return self._system(action, value)
            elif tool == "app":
                return self._app(action, value)
            elif tool == "keyboard":
                return self._keyboard(action, value)
            else:
                return f"Unknown tool: {tool}"

        except json.JSONDecodeError:
            logger.error(f"Invalid JSON: {json_string[:80]}")
            return "Failed to understand command."
        except Exception as e:
            logger.error(f"Execution error: {e}")
            return "Something went wrong."

    def _browser(self, action: str, value: str) -> str:
        """Browser actions."""
        if action == "open":
            if not value.startswith("http"):
                value = f"https://{value}"
            webbrowser.open(value)
            return f"Opening {value.replace('https://', '').split('/')[0]}"
        elif action == "search":
            webbrowser.open(f"https://www.google.com/search?q={value.replace(' ', '+')}")
            return f"Searching for {value}"
        return "Browser action failed."

    def _media(self, action: str, value: str) -> str:
        """Media control."""
        if action == "press":
            key = value.lower().replace(" ", "").replace("_", "")
            key_map = {
                "volumeup": "volumeup", "volumedown": "volumedown",
                "mute": "volumemute", "volumemute": "volumemute",
                "play": "playpause", "pause": "playpause", "playpause": "playpause",
                "next": "nexttrack", "nexttrack": "nexttrack",
                "prev": "prevtrack", "previous": "prevtrack",
            }
            actual_key = key_map.get(key, key)
            try:
                pyautogui.press(actual_key)
                return f"Volume adjusted." if "volume" in actual_key else "Media controlled."
            except Exception:
                return "Media control failed."
        return "Media action failed."

    def _system(self, action: str, value: str) -> str:
        """System commands."""
        value_lower = value.lower()
        
        if value_lower == "lock":
            os.system("rundll32.exe user32.dll,LockWorkStation")
            return "Locking workstation."
        elif value_lower == "sleep":
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            return "Putting PC to sleep."
        elif value_lower in ["exit", "quit", "shutdown", "goodbye", "stop"]:
            import sys
            print("\n🤖 JARVIS: Goodbye, Sir.")
            sys.exit(0)
        return "System command executed."

    def _app(self, action: str, value: str) -> str:
        """Launch apps using PowerShell (most reliable on Windows)."""
        if action in ["open", "launch", "start"]:
            app_name = value.lower().strip()
            display_name = value.capitalize()
            
            # Method 1: Direct PowerShell Start-Process (most reliable)
            try:
                # Check if it's a known app
                if app_name in COMMON_APPS:
                    exe = COMMON_APPS[app_name]
                    # Use PowerShell Start-Process which searches PATH and Start Menu
                    cmd = f'powershell -Command "Start-Process \'{exe}\' -ErrorAction SilentlyContinue"'
                    subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    return f"Opening {display_name}."
                
                # Method 2: Windows Run dialog (works for most apps)
                cmd = f'powershell -Command "Start-Process \'{app_name}\' -ErrorAction SilentlyContinue"'
                subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return f"Opening {display_name}."
                
            except Exception as e:
                logger.error(f"PowerShell launch failed: {e}")
            
            # Method 3: Fallback to shell:AppsFolder for modern apps
            try:
                # This opens the app via Windows shell
                subprocess.Popen(f'explorer shell:AppsFolder\\{app_name}', shell=True)
                return f"Opening {display_name}."
            except Exception:
                pass
            
            return f"Could not find {display_name}."
        
        elif action == "close":
            try:
                exe_name = value.lower().replace(" ", "")
                os.system(f"taskkill /IM {exe_name}.exe /F 2>nul")
                return f"Closing {value}."
            except Exception:
                return f"Could not close {value}."
        
        return "App action failed."

    def _keyboard(self, action: str, value: str) -> str:
        """Keyboard actions."""
        if action == "type":
            pyautogui.write(value)  # Use write() instead of typewrite()
            return "Typed text."
        elif action == "press":
            pyautogui.press(value)
            return f"Pressed {value}."
        elif action == "hotkey":
            keys = [k.strip() for k in value.split("+")]
            pyautogui.hotkey(*keys)
            return f"Pressed {value}."
        return "Keyboard action failed."


# Singleton
d_hands = Hands()
