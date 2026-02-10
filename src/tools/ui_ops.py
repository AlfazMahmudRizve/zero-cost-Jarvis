"""
UI Automation Tool (The Hands v2)
Uses Microsoft UI Automation to interact with application windows reliably.
File: src/tools/ui_ops.py
"""

import uiautomation as auto
import subprocess
from src.core.logger import get_logger

logger = get_logger(__name__)

class DesktopController:
    def __init__(self):
        auto.SetGlobalSearchTimeout(2)  # 2s timeout

    def click_button_by_text(self, app_name: str, button_name: str) -> str:
        """
        Find an app window and click a button by text.
        """
        logger.info(f"UI: Clicking '{button_name}' in '{app_name}'")
        
        # 1. Find Main Window
        window = auto.WindowControl(searchDepth=1, Name=app_name, RegexName=True)
        
        if not window.Exists(0):
            return f"I can't find '{app_name}'. Is it open?"

        # 2. Focus
        try:
            if window.MinimizeState:
                window.Restore()
            window.SetFocus()
        except Exception as e:
            logger.warning(f"Could not focus window: {e}")

        # 3. Find Button
        btn = window.ButtonControl(Name=button_name)
        
        if btn.Exists(0):
            btn.Click()
            return f"Clicked '{button_name}' in {app_name}."
        
        # Fallback: Generic Control
        item = window.Control(Name=button_name)
        if item.Exists(0):
            item.Click()
            return f"Clicked '{button_name}' (Generic)."
            
        return f"Found {app_name}, but no button named '{button_name}'."

    def scan_app(self, app_name: str) -> str:
        """
        Scan an app window and list accessible elements.
        """
        window = auto.WindowControl(searchDepth=1, Name=app_name, RegexName=True)
        if not window.Exists(0):
            return f"App '{app_name}' not found."
            
        elements = []
        count = 0
        for item in window.GetChildren():
            if count > 50: break
            if item.Name:
                elements.append(f"- {item.Name} ({item.ControlTypeName})")
            count += 1
            
        return f"--- Scan of {app_name} ---\n" + "\n".join(elements)

# Singleton
d_desktop = DesktopController()

def ui_click(app: str, target: str) -> str:
    return d_desktop.click_button_by_text(app, target)

def ui_scan(app: str) -> str:
    return d_desktop.scan_app(app)
