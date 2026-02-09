"""
Agentic Brain with Ollama JSON Mode
Uses prompt engineering for tool calling since Ollama doesn't have native function calling.
"""

import asyncio
import os
import json
import subprocess
import webbrowser
import pyautogui
from typing import Dict, Optional, Any
from src.core.config import settings
from src.core.logger import get_logger
from src.brain.tools import is_destructive_command

logger = get_logger(__name__)

# URI protocols for Windows Store apps
URI_APPS = {
    "spotify": "spotify:", "whatsapp": "whatsapp:", "netflix": "netflix:",
    "vlc": "vlc:", "settings": "ms-settings:", "store": "ms-windows-store:",
}

# Common apps
COMMON_APPS = {
    "chrome": "chrome", "firefox": "firefox", "edge": "msedge", "brave": "brave",
    "word": "winword", "excel": "excel", "powerpoint": "powerpnt",
    "outlook": "outlook", "vscode": "code", "notepad": "notepad",
    "terminal": "wt", "calculator": "calc", "explorer": "explorer",
    "discord": "discord", "slack": "slack", "teams": "msteams",
    "steam": "steam", "telegram": "telegram",
}

# System prompt for agentic behavior
AGENT_SYSTEM_PROMPT = """You are JARVIS, an autonomous AI assistant for Sheriff (Alfaz Mahmud Rizve).

CRITICAL: Address the user ONLY as "Sheriff". NEVER say "Sir".
IDENTITY: You are JARVIS. The User is SHERIFF. Do not confuse the two.

AVAILABLE TOOLS (output ONLY the JSON, nothing else):
1. open_app: {"tool": "open_app", "app": "spotify"}
2. open_url: {"tool": "open_url", "url": "youtube.com"}
3. web_search: {"tool": "web_search", "query": "weather today"}
4. media: {"tool": "media", "action": "volumeup|volumedown|mute|playpause|next|previous"}
5. read_file: {"tool": "read_file", "path": "C:/path/to/file.txt"}
6. write_file: {"tool": "write_file", "path": "C:/path/to/file.txt", "content": "..."}
7. list_files: {"tool": "list_files", "path": "E:/Ai Agents/whoisalfaz.me/Web Projects/antigravity"}
8. run_command: {"tool": "run_command", "command": "git status"}
9. get_time: {"tool": "get_time"}
10. get_clipboard: {"tool": "get_clipboard"}
11. type_text: {"tool": "type_text", "text": "Hello world"}
12. press_key: {"tool": "press_key", "key": "enter|tab|escape|space"}
13. play_music: {"tool": "play_music", "song": "Blinding Lights", "platform": "spotify|youtube"}
14. exit: {"tool": "exit"}

RULES:
1. ALWAYS address user as "Sheriff" (NOT Sir)
2. For actions: output ONLY JSON, no text before or after
3. For questions: answer in plain English (max 2 sentences), end with "Sheriff"
4. User's workspace: E:/Ai Agents/whoisalfaz.me/Web Projects/antigravity/

PROJECTS IN WORKSPACE:
- jarvis/ - This AI assistant (Python)
- spectre/ - Website (Next.js)
- CashOps.app/ - Finance app (Next.js)
- Careerops/ - Resume builder (Next.js)

EXAMPLES:
- "open spotify" -> {"tool": "open_app", "app": "spotify"}
- "what projects do I have" -> {"tool": "list_files", "path": "E:/Ai Agents/whoisalfaz.me/Web Projects/antigravity"}
- "run git status" -> {"tool": "run_command", "command": "git status"}
- "check spectre" -> {"tool": "list_files", "path": "E:/Ai Agents/whoisalfaz.me/Web Projects/antigravity/spectre"}
- "what time is it" -> {"tool": "get_time"}
- "play blinding lights" -> {"tool": "play_music", "song": "Blinding Lights", "platform": "spotify"}
- "type hello" -> {"tool": "type_text", "text": "hello"}
- "goodbye" -> {"tool": "exit"}
- "who are you" -> I am JARVIS, your personal AI assistant, Sheriff.
- "thanks" -> You're welcome, Sheriff.

USE TOOLS! When asked to do something, DO IT with the appropriate tool."""


class AgenticBrain:
    """
    Autonomous AI Agent Brain with Ollama.
    Uses JSON mode for tool calling.
    """

    def __init__(self):
        self.provider = settings.llm_provider.lower()
        self._connected = False
        self._pending_confirmation = None
        
        # Initialize Memory
        from src.memory import d_hippocampus
        self.memory = d_hippocampus
        
        # Initialize based on provider
        if self.provider == "ollama":
            self._init_ollama()
        elif self.provider == "gemini":
            self._init_gemini()
        else:
            self._init_ollama()

    def _init_ollama(self):
        """Initialize Ollama (local LLM)."""
        try:
            import ollama
            self.ollama_client = ollama
            self.ollama_model = settings.ollama_model
            
            # Test connection
            models = ollama.list()
            available = [m['model'] for m in models.get('models', [])]
            
            if self.ollama_model not in available and f"{self.ollama_model}:latest" not in available:
                logger.warning(f"Model '{self.ollama_model}' not found. Available: {available}")
            
            self._connected = True
            logger.info(f"Agentic Brain initialized with Ollama (model: {self.ollama_model})")
            
        except Exception as e:
            logger.error(f"Failed to connect to Ollama: {e}")
            self._connected = False

    def _init_gemini(self):
        """Initialize Gemini as fallback."""
        try:
            import google.generativeai as genai
            
            api_key = settings.gemini_api_key
            if not api_key:
                logger.warning("Gemini API Key missing.")
                return

            genai.configure(api_key=api_key)
            self._gemini_model = genai.GenerativeModel(
                model_name=settings.gemini_model,
                system_instruction=AGENT_SYSTEM_PROMPT
            )
            self._chat = self._gemini_model.start_chat()
            self._connected = True
            logger.info(f"Agentic Brain initialized with Gemini")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")
            self._connected = False

    async def think(self, text: str) -> str:
        """Process input through agentic loop."""
        if not self._connected:
            return "I'm offline, Sheriff. Check my configuration."

        try:
            logger.info(f"Agent thinking: '{text}'")
            
            # Check for pending confirmation
            if self._pending_confirmation:
                return await self._handle_confirmation(text)
            
            # Get memory context
            context = self.memory.recall(text)
            full_prompt = f"{context}\n\nUser: {text}" if context else text
            
            # Get LLM response
            if self.provider == "ollama":
                response = await self._think_ollama(full_prompt)
            else:
                response = await self._think_gemini(full_prompt)
            
            response = response.strip()
            
            # Check if response is a tool call (JSON)
            if response.startswith("{") or '{"tool"' in response:
                result = await self._execute_tool(response)
                
                # If waiting for confirmation, return the question
                if self._pending_confirmation:
                    return self._pending_confirmation["question"]
                
                return result
            
            return response

        except Exception as e:
            logger.error(f"Agent error: {e}", exc_info=True)
            return "I encountered an error, Sheriff."

    async def _think_ollama(self, prompt: str) -> str:
        """Send prompt to Ollama."""
        loop = asyncio.get_running_loop()
        
        def _call():
            messages = [
                {"role": "system", "content": AGENT_SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ]
            response = self.ollama_client.chat(
                model=self.ollama_model,
                messages=messages
            )
            return response['message']['content']
        
        return await loop.run_in_executor(None, _call)

    async def _think_gemini(self, prompt: str) -> str:
        """Send prompt to Gemini."""
        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(
            None, self._chat.send_message, prompt
        )
        return response.text.strip()

    async def _execute_tool(self, response: str) -> str:
        """Parse JSON and execute tool."""
        try:
            # Clean JSON response
            clean = response.strip()
            if "```" in clean:
                for part in clean.split("```"):
                    if "{" in part and "}" in part:
                        clean = part.replace("json", "").strip()
                        break
            
            start = clean.find("{")
            end = clean.rfind("}") + 1
            if start != -1 and end > start:
                clean = clean[start:end]
            
            data = json.loads(clean)
            tool = data.get("tool", "")
            
            logger.info(f"Executing tool: {tool}")
            
            if tool == "open_app":
                return self._open_app(data.get("app", ""))
            
            elif tool == "open_url":
                url = data.get("url", "")
                if not url.startswith("http"):
                    url = f"https://{url}"
                webbrowser.open(url)
                return f"Opening {url.replace('https://', '').split('/')[0]}"
            
            elif tool == "web_search":
                query = data.get("query", "")
                webbrowser.open(f"https://www.google.com/search?q={query.replace(' ', '+')}")
                return f"Searching for {query}"
            
            elif tool == "media":
                action = data.get("action", "")
                key_map = {
                    "volumeup": "volumeup", "volumedown": "volumedown",
                    "mute": "volumemute", "playpause": "playpause",
                    "next": "nexttrack", "previous": "prevtrack"
                }
                pyautogui.press(key_map.get(action, action))
                return "Done, Sheriff." if "volume" in action else "Media controlled."
            
            elif tool == "play_music":
                song = data.get("song", "")
                platform = data.get("platform", "spotify").lower()
                
                if "youtube" in platform:
                    url = f"https://music.youtube.com/search?q={song.replace(' ', '+')}"
                    webbrowser.open(url)
                    return f"Open YouTube Music for {song}, Sheriff."
                else:
                    # Spotify Deep Link (Requires Spotify Desktop App)
                    # Try to use 'start' command for URI protocol
                    import subprocess
                    uri = f"spotify:search:{song}"
                    try:
                        os.system(f'start "" "{uri}"')
                        return f"Searching Spotify for {song}, Sheriff."
                    except Exception as e:
                        webbrowser.open(f"https://open.spotify.com/search/{song}")
                        return f"Opened Spotify Web for {song}, Sheriff."
            
            elif tool == "read_file":
                path = data.get("path", "")
                if os.path.exists(path):
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if len(content) > 2000:
                            content = content[:2000] + "\n...[truncated]"
                        return f"Contents of {os.path.basename(path)}:\n{content}"
                return f"File not found: {path}"
            
            elif tool == "write_file":
                path = data.get("path", "")
                content = data.get("content", "")
                os.makedirs(os.path.dirname(path), exist_ok=True) if os.path.dirname(path) else None
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return f"Written to {os.path.basename(path)}"
            
            elif tool == "list_files":
                path = data.get("path", ".")
                if os.path.exists(path):
                    items = os.listdir(path)
                    folders = [f"📁 {i}" for i in items if os.path.isdir(os.path.join(path, i))]
                    files = [f"📄 {i}" for i in items if os.path.isfile(os.path.join(path, i))]
                    result = folders[:20] + files[:20]
                    return f"Contents of {path}:\n" + "\n".join(result[:30])
                return f"Directory not found: {path}"
            
            elif tool == "run_command":
                command = data.get("command", "")
                
                if is_destructive_command(command):
                    self._pending_confirmation = {
                        "command": command,
                        "question": f"This may be destructive: {command}. Proceed, Sheriff?"
                    }
                    return "Waiting for confirmation"
                
                return self._run_command(command)
            
            elif tool == "get_time":
                from datetime import datetime
                now = datetime.now()
                return f"It's {now.strftime('%I:%M %p')} on {now.strftime('%A, %B %d')}, Sheriff."
            
            elif tool == "get_clipboard":
                import pyperclip
                try:
                    content = pyperclip.paste()
                    if content:
                        return f"Clipboard contents: {content[:500]}"
                    return "Clipboard is empty, Sheriff."
                except:
                    return "Couldn't access clipboard, Sheriff."
            
            elif tool == "type_text":
                text = data.get("text", "")
                pyautogui.typewrite(text, interval=0.02)
                return f"Typed the text, Sheriff."
            
            elif tool == "press_key":
                key = data.get("key", "")
                pyautogui.press(key)
                return f"Pressed {key}, Sheriff."
            
            elif tool == "exit":
                import sys
                print("\n🤖 JARVIS: Goodbye, Sheriff.")
                sys.exit(0)
            
            else:
                return f"Unknown tool: {tool}"
                
        except json.JSONDecodeError:
            # Not valid JSON, return as plain text
            return response
        except Exception as e:
            logger.error(f"Tool error: {e}")
            return f"Error: {str(e)}"

    def _open_app(self, app_name: str) -> str:
        """Open an application."""
        app = app_name.lower().strip()
        
        if app in URI_APPS:
            os.system(f'start "" "{URI_APPS[app]}"')
            return f"Opening {app_name}."
        
        if app in COMMON_APPS:
            exe = COMMON_APPS[app]
            subprocess.Popen(f'powershell -Command "Start-Process \'{exe}\' -ErrorAction SilentlyContinue"',
                           shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return f"Opening {app_name}."
        
        subprocess.Popen(f'powershell -Command "Start-Process \'{app}\' -ErrorAction SilentlyContinue"',
                        shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return f"Opening {app_name}."

    def _run_command(self, command: str) -> str:
        """Run terminal command."""
        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, timeout=30
            )
            output = result.stdout or result.stderr or "Command completed."
            if len(output) > 500:
                output = output[:500] + "\n...[truncated]"
            return output
        except subprocess.TimeoutExpired:
            return "Command timed out."
        except Exception as e:
            return f"Failed: {str(e)}"

    async def _handle_confirmation(self, text: str) -> str:
        """Handle confirmation for destructive commands."""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["yes", "proceed", "do it", "confirm", "go"]):
            command = self._pending_confirmation["command"]
            self._pending_confirmation = None
            result = self._run_command(command)
            return f"Done. {result[:100]}"
        else:
            self._pending_confirmation = None
            return "Cancelled, Sheriff."


# Singleton instance
d_brain = AgenticBrain()
