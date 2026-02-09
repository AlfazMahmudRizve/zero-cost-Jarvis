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

# Common apps - Use URI protocols for Windows Store apps
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
    # Communication
    "discord": "discord", "slack": "slack", "teams": "msteams",
    "zoom": "zoom", "telegram": "telegram",
    # Other
    "steam": "steam", "obs": "obs64",
}

# Windows Store apps use URI protocols
URI_APPS = {
    "spotify": "spotify:",
    "whatsapp": "whatsapp:",
    "netflix": "netflix:",
    "vlc": "vlc:",
    "settings": "ms-settings:",
    "store": "ms-windows-store:",
    "mail": "mailto:",
    "calendar": "outlookcal:",
    "photos": "ms-photos:",
    "camera": "microsoft.windows.camera:",
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
        """System commands - RESTRICTED for safety."""
        value_lower = value.lower()
        
        # Only allow Jarvis to shut itself off
        if value_lower in ["exit", "quit", "shutdown", "goodbye", "stop", "bye"]:
            import sys
            print("\n🤖 JARVIS: Goodbye, Sheriff.")
            sys.exit(0)
        
        # Block all other system commands for safety
        return "I cannot perform system control actions, Sheriff."

    def _app(self, action: str, value: str) -> str:
        """Launch apps - supports both regular apps and Windows Store apps."""
        if action in ["open", "launch", "start"]:
            app_name = value.lower().strip()
            display_name = value.capitalize()
            
            # Method 1: Check URI protocols for Windows Store apps (Spotify, etc.)
            if app_name in URI_APPS:
                uri = URI_APPS[app_name]
                try:
                    cmd = f'powershell -Command "Start-Process \'{uri}\'"'
                    subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    return f"Opening {display_name}."
                except Exception as e:
                    logger.error(f"URI launch failed: {e}")
            
            # Method 2: Check regular apps
            if app_name in COMMON_APPS:
                exe = COMMON_APPS[app_name]
                try:
                    cmd = f'powershell -Command "Start-Process \'{exe}\' -ErrorAction SilentlyContinue"'
                    subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    return f"Opening {display_name}."
                except Exception as e:
                    logger.error(f"App launch failed: {e}")
            
            # Method 3: Try direct name
            try:
                cmd = f'powershell -Command "Start-Process \'{app_name}\' -ErrorAction SilentlyContinue"'
                subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
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
