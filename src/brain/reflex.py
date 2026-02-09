"""
Reflex Layer (The Spine)
Handles immediate, non-cognitive actions to bypass the LLM for speed.
"""

import re
import os
import webbrowser
import subprocess
from src.core.logger import get_logger
from src.senses.tts import d_tts

logger = get_logger(__name__)

class ReflexSpine:
    def __init__(self):
        # Compiled regex patterns for speed
        self.patterns = {
            "stop": re.compile(r"^(stop|quiet|silence|shut up|mute)$", re.IGNORECASE),
            "open_url": re.compile(r"^open (google|youtube|reddit|github|gmail|mail)(?:\.com)?$", re.IGNORECASE),
            "open_app": re.compile(r"^open (calc|calculator|notepad|cmd|terminal|explorer|spotify|code|vscode)$", re.IGNORECASE),
            "time": re.compile(r"^(what time is it|time check|current time)$", re.IGNORECASE),
        }

    async def check_reflex(self, command: str) -> bool:
        """
        Check if command matches a reflex pattern.
        If yes, execute immediately and return True.
        """
        command = command.strip()
        
        # 1. Stop/Silence (Highest Priority)
        if self.patterns["stop"].match(command):
            logger.info(f"Reflex triggered: STOP")
            d_tts.stop() # Kill audio
            return True

        # 2. Open Common URLs
        match = self.patterns["open_url"].match(command)
        if match:
            target = match.group(1).lower()
            url = f"https://www.{target}.com" if "." not in target else f"https://{target}"
            if target == "gmail" or target == "mail":
                url = "https://mail.google.com"
            
            logger.info(f"Reflex triggered: OPEN URL {url}")
            await d_tts.speak(f"Opening {target}.")
            webbrowser.open(url)
            return True

        # 3. Open Common Apps
        match = self.patterns["open_app"].match(command)
        if match:
            app = match.group(1).lower()
            logger.info(f"Reflex triggered: OPEN APP {app}")
            await d_tts.speak(f"Opening {app}.")
            
            if app in ["calc", "calculator"]:
                subprocess.Popen("calc")
            elif app == "notepad":
                subprocess.Popen("notepad")
            elif app in ["cmd", "terminal"]:
                subprocess.Popen("wt") # Windows Terminal
            elif app == "explorer":
                subprocess.Popen("explorer")
            elif app == "spotify":
                os.system("start spotify:")
            elif app in ["code", "vscode"]:
                subprocess.Popen("code")
            return True

        # 4. Time Check
        if self.patterns["time"].match(command):
            from datetime import datetime
            now = datetime.now().strftime("%I:%M %p")
            logger.info(f"Reflex triggered: TIME")
            await d_tts.speak(f"It is {now}.")
            return True

        # 5. Volume Control (PowerShell)
        if "volume up" in command or "turn it up" in command:
            logger.info("Reflex: Volume Up")
            subprocess.Popen(["powershell", "-c", "(New-Object -ComObject WScript.Shell).SendKeys([char]175)"]) 
            return True
            
        if "volume down" in command or "turn it down" in command or "turn down" in command:
            logger.info("Reflex: Volume Down")
            for _ in range(3): # Lower it significantly
                subprocess.Popen(["powershell", "-c", "(New-Object -ComObject WScript.Shell).SendKeys([char]174)"]) 
            return True
            
        if "mute" in command or "unmute" in command:
            logger.info("Reflex: Mute/Unmute")
            subprocess.Popen(["powershell", "-c", "(New-Object -ComObject WScript.Shell).SendKeys([char]173)"]) 
            return True

        return False

# Singleton
d_spine = ReflexSpine()
