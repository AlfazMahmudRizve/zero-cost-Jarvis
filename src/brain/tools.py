"""
Tool Definitions for the Agentic Brain
Defines all tools that JARVIS can use with function calling.
"""

# Tool schemas for Gemini function calling
TOOL_DEFINITIONS = [
    {
        "name": "open_app",
        "description": "Open/launch an application on the PC. Examples: spotify, chrome, vscode, discord, notepad, calculator.",
        "parameters": {
            "type": "object",
            "properties": {
                "app_name": {
                    "type": "string",
                    "description": "Name of the app to open (e.g., 'spotify', 'chrome', 'vscode')"
                }
            },
            "required": ["app_name"]
        }
    },
    {
        "name": "open_browser",
        "description": "Open a website URL in the default browser.",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "URL to open (e.g., 'youtube.com', 'github.com')"
                }
            },
            "required": ["url"]
        }
    },
    {
        "name": "web_search",
        "description": "Search the web using Google.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "control_media",
        "description": "Control media playback and volume. Actions: volumeup, volumedown, mute, playpause, next, previous.",
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["volumeup", "volumedown", "mute", "playpause", "next", "previous"],
                    "description": "Media action to perform"
                }
            },
            "required": ["action"]
        }
    },
    {
        "name": "read_file",
        "description": "Read the contents of a file. Use for checking code, configs, or documents.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the file to read"
                }
            },
            "required": ["file_path"]
        }
    },
    {
        "name": "write_file",
        "description": "Write content to a file. Creates new file or overwrites existing.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the file to write"
                },
                "content": {
                    "type": "string",
                    "description": "Content to write to the file"
                }
            },
            "required": ["file_path", "content"]
        }
    },
    {
        "name": "list_files",
        "description": "List files and directories in a folder.",
        "parameters": {
            "type": "object",
            "properties": {
                "directory": {
                    "type": "string",
                    "description": "Path to directory to list"
                }
            },
            "required": ["directory"]
        }
    },
    {
        "name": "run_terminal",
        "description": "Execute a terminal/shell command. Use for git, npm, python, etc. CAUTION: Destructive commands will ask for confirmation.",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "Shell command to execute"
                }
            },
            "required": ["command"]
        }
    },
    {
        "name": "exit_jarvis",
        "description": "Shut down JARVIS. Use when user says goodbye or wants to stop.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
]

# Destructive commands that require confirmation
DESTRUCTIVE_PATTERNS = [
    "rm ", "del ", "rmdir", "remove", "delete",
    "format", "fdisk", 
    "drop ", "truncate",
    "shutdown", "restart", "reboot",
    "> ", ">>",  # redirect that overwrites
    "git push --force", "git reset --hard",
]

def is_destructive_command(command: str) -> bool:
    """Check if a command is potentially destructive."""
    cmd_lower = command.lower()
    return any(pattern in cmd_lower for pattern in DESTRUCTIVE_PATTERNS)
