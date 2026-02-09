"""
Vision Module (The Eyes)
Uses Ollama (moondream) to analyze screenshots.
"""

import io
import base64
import pyautogui
from PIL import Image
import ollama
from src.core.logger import get_logger

logger = get_logger(__name__)

VISION_MODEL = "moondream"

def analyze_screen(prompt: str = "Describe what is on the screen.") -> str:
    """
    Captures the screen and asks the vision model to analyze it.
    Args:
        prompt: Question about the screen.
    Returns:
        Analysis text.
    """
    try:
        logger.info(f"Vision: capturing screen for prompt: '{prompt}'")
        
        # 1. Capture Screenshot
        screenshot = pyautogui.screenshot()
        
        # 2. Optimize image (Resize to max 1024x1024 for speed/context limit)
        screenshot.thumbnail((1024, 1024))
        
        # 3. Convert to bytes buffer
        img_buffer = io.BytesIO()
        screenshot.save(img_buffer, format='JPEG', quality=85)
        img_bytes = img_buffer.getvalue()
        
        # 4. Query Ollama
        logger.info(f"Vision: sending to {VISION_MODEL}...")
        response = ollama.chat(
            model=VISION_MODEL,
            messages=[{
                'role': 'user',
                'content': prompt,
                'images': [img_bytes]
            }]
        )
        
        result = response.get('message', {}).get('content', '')
        if not result:
            return "I couldn't enhance the image, Sheriff."
            
        logger.info(f"Vision Result: {result[:50]}...")
        return f"I see: {result}"

    except ollama.ResponseError as e:
        if e.status_code == 404:
            return f"Error: Model '{VISION_MODEL}' not found. Run 'ollama pull {VISION_MODEL}'."
        return f"Vision Error: {str(e)}"
    except Exception as e:
        logger.error(f"Vision Failed: {e}")
        return f"failed to analyze screen: {str(e)}"
