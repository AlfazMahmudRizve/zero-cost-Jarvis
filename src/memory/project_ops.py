"""
Project Ops (The Manager)
Manages .sheriff ledger files for project context and task tracking.
"""

import os
from typing import Optional
from src.core.logger import get_logger

logger = get_logger(__name__)

# Project Registry: Alias -> Absolute Path
PROJECT_PATHS = {
    "jarvis": r"e:\Ai Agents\whoisalfaz.me\Web Projects\antigravity\jarvis",
    "spectre": r"e:\Ai Agents\whoisalfaz.me\Web Projects\antigravity\spectre",
    "cashops": r"e:\Ai Agents\whoisalfaz.me\Web Projects\antigravity\CashOps.app",
    "careerops": r"e:\Ai Agents\whoisalfaz.me\Web Projects\antigravity\Careerops"
}

# Global State for current project context
current_project = {
    "alias": None,
    "path": None
}

DEFAULT_TEMPLATE = """# PROJECT: {name}
# GOAL: [One sentence goal]
# DEADLINE: [Date]
# MOTIVATION: [Why is this important?]

## STATUS (Last Updated: {date})
- [ ] Initial Task

## CONTEXT & BLOCKERS
- Current issue: None
- Tech Stack: [Stack]
- Notes: None
"""

def get_project_path(alias: str) -> Optional[str]:
    """Returns absolute path for project alias."""
    return PROJECT_PATHS.get(alias.lower())

def load_project_context(alias: str) -> str:
    """
    Loads .sheriff file from project root.
    If missing, creates a default template.
    """
    path = get_project_path(alias)
    if not path or not os.path.exists(path):
        return f"Project '{alias}' not found in registry."

    # Update global state
    current_project["alias"] = alias
    current_project["path"] = path
    
    sheriff_file = os.path.join(path, ".sheriff")
    
    if os.path.exists(sheriff_file):
        try:
            with open(sheriff_file, "r", encoding="utf-8") as f:
                content = f.read()
            return f"Context loaded for {alias}:\n{content}"
        except Exception as e:
            return f"Error reading .sheriff file: {e}"
    else:
        # Create default
        from datetime import datetime
        content = DEFAULT_TEMPLATE.format(
            name=alias.capitalize(),
            date=datetime.now().strftime("%Y-%m-%d")
        )
        try:
            with open(sheriff_file, "w", encoding="utf-8") as f:
                f.write(content)
            return f"Initialized new project ledger for {alias}. Please update the goals."
        except Exception as e:
            return f"Error creating .sheriff file: {e}"

def add_task(task: str) -> str:
    """Appends a task to the current .sheriff file."""
    if not current_project["path"]:
        return "No project loaded. Use 'load_project_context' first."
        
    sheriff_file = os.path.join(current_project["path"], ".sheriff")
    if not os.path.exists(sheriff_file):
        return "Internal Error: .sheriff file missing."
        
    try:
        # Read lines
        with open(sheriff_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        # Find ## STATUS section
        status_index = -1
        for i, line in enumerate(lines):
            if "## STATUS" in line:
                status_index = i
                break
        
        entry = f"- [ ] {task}\n"
        
        if status_index != -1:
            # Insert after STATUS line
            lines.insert(status_index + 1, entry)
        else:
            # Append if section missing (fallback)
            lines.append("\n## STATUS\n")
            lines.append(entry)
            
        # Verify Context section exists, if not append it
        if not any("## CONTEXT" in line for line in lines):
             lines.append("\n## CONTEXT & BLOCKERS\n- Current issue: None\n")
             
        # Write back
        with open(sheriff_file, "w", encoding="utf-8") as f:
            f.writelines(lines)
            
        return f"Added task: {task}"
        
    except Exception as e:
        return f"Failed to add task: {e}"

def log_blocker(issue: str) -> str:
    """Updates 'Current issue' in .sheriff file."""
    if not current_project["path"]:
        return "No project loaded."
        
    sheriff_file = os.path.join(current_project["path"], ".sheriff")
    
    try:
        with open(sheriff_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        # Simple replacement logic
        new_lines = []
        updated = False
        for line in lines:
            if line.strip().startswith("- Current issue:"):
                new_lines.append(f"- Current issue: {issue}\n")
                updated = True
            else:
                new_lines.append(line)
        
        if not updated:
            # Append if missing
            new_lines.append(f"- Current issue: {issue}\n")

        with open(sheriff_file, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
            
        return f"Logged blocker: {issue}"
        
    except Exception as e:
        return f"Failed to log blocker: {e}"

def mark_complete(task_keyword: str) -> str:
    """Marks a task as complete if it matches the keyword."""
    if not current_project["path"]:
        return "No project loaded."
        
    try:
        sheriff_file = os.path.join(current_project["path"], ".sheriff")
        with open(sheriff_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        updated_count = 0
        new_lines = []
        for line in lines:
            if "- [ ]" in line and task_keyword.lower() in line.lower():
                new_lines.append(line.replace("- [ ]", "- [x]"))
                updated_count += 1
            else:
                new_lines.append(line)
                
        with open(sheriff_file, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
            
        if updated_count > 0:
            return f"Marked {updated_count} task(s) as complete."
        else:
            return f"No task found matching '{task_keyword}'."
            
    except Exception as e:
        return f"Error: {e}"
