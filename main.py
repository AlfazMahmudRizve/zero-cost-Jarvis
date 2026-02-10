"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║       ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗                                ║
║       ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝                                ║
║       ██║███████║██████╔╝██║   ██║██║███████╗                                ║
║  ██   ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║                                ║
║  ╚█████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║                                ║
║   ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝                                ║
║                                                                               ║
║         Zero-Cost AI Assistant v3.2 (The HUD Upgrade)                         ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝

Entry point for JARVIS AI Assistant.
Orchestrates the Senses, Brain, Memory, Hands, and the Visual Cortex (HUD).
"""

import asyncio
import signal
import sys
import json
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.config import settings
from src.core.logger import (
    setup_logging,
    get_logger,
    console,
    jarvis_speak,
    success_message,
    error_message,
    warning_message,
)
from src.core.exceptions import JarvisError

# Import Singletons
from src.senses import d_stt, d_tts
from src.brain import d_brain
from src.memory import d_hippocampus
from src.tools import d_hands
from src.senses.ears_v2 import NaturalEars
from src.brain.reflex import d_spine
import re

# Import UI
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QThread, pyqtSignal, QObject
from src.ui.hud import JarvisHUD

logger = get_logger(__name__)


def print_banner() -> None:
    """Print the JARVIS startup banner."""
    banner = """
[blue bold]
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║       ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗                ║
    ║       ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝                ║
    ║       ██║███████║██████╔╝██║   ██║██║███████╗                ║
    ║  ██   ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║                ║
    ║  ╚█████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║                ║
    ║   ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝                ║
    ║                                                               ║
    ║         [cyan]Zero-Cost AI Assistant v3.3[/cyan]                         ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
[/blue bold]
"""
    console.print(banner)


class JarvisWorker(QThread):
    """
    Background worker thread running the main agent loop.
    Emits signals to update the UI.
    """
    state_signal = pyqtSignal(str) # "IDLE", "LISTENING", "PROCESSING", "SPEAKING"
    text_signal = pyqtSignal(str)  # Updates the text label
    
    def run(self):
        """Entry point for the thread."""
        asyncio.run(self.agent_loop())
        
    async def agent_loop(self):
        """
        Main orchestration loop:
        Listen (Latch) -> VAD -> Transcribe -> Wake/Command -> Act -> Speak -> Keep Latch
        """
        jarvis_speak("Ready for your command, Sheriff.")
        self.state_signal.emit("IDLE")
        self.text_signal.emit("Online - Waiting for command")
        
        self.is_speaking = False
        
        # Initialize Ears
        ears = NaturalEars()
        
        wake_word_variants = [
            "jarvis", "darius", "jervis", "jarv", "jaravis", "jarvi", 
            "service", "harvest", "travis", "davis", "chavis", 
            "chief"
        ]
        
        while True:
            try:
                # 1. LISTEN (With Latch Check)
                is_latched = ears.check_latch()
                
                if is_latched:
                    self.state_signal.emit("LISTENING")
                    self.text_signal.emit("Listening (Latched)...")
                else:
                    self.state_signal.emit("IDLE")
                    self.text_signal.emit("Waiting for Wake Word...")
                
                # listen() blocks until speech is detected and finished
                audio_buffer = await ears.listen()
                
                if len(audio_buffer) == 0:
                    continue

                # 2. TRANSCRIBE
                text = await d_stt.transcribe(audio_buffer)
                
                if not text:
                    continue
                
                # --- SANITATION ---
                # Remove punctuation to prevent "Jarvis." -> "." -> Hallucination
                clean_text = re.sub(r'[^\w\s]', '', text).strip()
                if not clean_text:
                    continue
                # ------------------
                
                text_lower = clean_text.lower()
                logger.info(f"Heard (Clean): '{clean_text}'")
                self.text_signal.emit(f"Heard: {clean_text}")

                # 3. LOGIC & WAKE WORD
                command = ""
                
                if is_latched:
                    command = clean_text
                    logger.info(f"Latched command: {command}")
                else:
                    # Wake Word Check on CLEAN text
                    wake_detected = any(variant in text_lower for variant in wake_word_variants)
                    if wake_detected:
                        for variant in wake_word_variants:
                            if variant in text_lower:
                                # Split only on the first occurrence
                                parts = text_lower.split(variant, 1)
                                if len(parts) > 1:
                                    command = parts[1].strip()
                                else:
                                    command = ""
                                break
                        
                        # If command is empty (e.g. just "Jarvis"), acknowledge but don't act
                        if not command:
                            self.text_signal.emit("Yes, Sheriff?")
                            # Activate latch to listen for follow-up
                            ears.activate_latch()
                            continue
                    else:
                        continue # Ignore noise

                # Re-Sanitize Command (just in case)
                command = command.strip()
                if not command: continue

                # 4. REFLEX LAYER (The Spine)
                # Check for instant actions (Stop, Open X)
                # Pass LOWER case to reflex for matching (insensitive)
                if await d_spine.check_reflex(command.lower()):
                    # If reflex handled it, loop back immediately
                    self.text_signal.emit(f"Reflex: {command}")
                    
                    # If Stop Command, ensure we reset speaking state
                    if "stop" in command.lower():
                        self.is_speaking = False
                        
                    ears.activate_latch() # Keep flow open
                    continue
                    
                # BARGE-IN GUARD:
                # If JARVIS is speaking or Music is playing, IGNORE everything else to prevent echo loops.
                # Only Reflex (above) can interrupt.
                from src.tools.music import is_music_playing
                
                if self.is_speaking or is_music_playing():
                    logger.info(f"Ignored '{command}' because audio is active (Barge-In Guard).")
                    continue
                
                # 5. EXECUTION (The Brain)
                self.state_signal.emit("PROCESSING")
                self.text_signal.emit("Thinking...")
                
                response = await d_brain.think(command)
                self.state_signal.emit("SPEAKING")
                self.text_signal.emit(response)
                
                # Wrapper to track speaking state
                async def speak_task(text):
                    self.is_speaking = True
                    try:
                        await d_tts.speak(text)
                    finally:
                        self.is_speaking = False

                # NON-BLOCKING SPEAK (Fire & Forget) allows Barge-In
                asyncio.create_task(speak_task(response))
                
                d_hippocampus.memorize(f"User: {command} | JARVIS: {response[:100]}", "interaction")
                
                # Re-activate latch after speaking for flow
                ears.activate_latch()
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Loop error: {e}", exc_info=True)
                self.text_signal.emit(f"Error: {e}")
                self.is_speaking = False # Reset on error
                await asyncio.sleep(1.0) # Backoff


def main() -> None:
    """Main entry point."""
    # Setup Logging
    setup_logging(level=settings.log_level)
    print_banner()
    
    # Initialize UI
    app = QApplication(sys.argv)
    
    # Verify Config
    if not settings.active_llm_provider:
        error_message("No LLM API Key found! Please configure .env")
        sys.exit(1)
        
    success_message("Initializing HUD...")
    hud = JarvisHUD()
    
    success_message("Starting Core Systems...")
    
    success_message("Starting Core Systems...")
    
    # Initialize Journal
    from src.memory.journal import log
    log("SYSTEM", "Sheriff v5.0 (Architect) Online")
    
    # Initialize Worker
    worker = JarvisWorker()
    
    # Connect Signals
    worker.state_signal.connect(hud.update_state)
    worker.text_signal.connect(hud.update_text)
    
    # Start Worker
    worker.start()
    
    # Run UI Loop
    try:
        sys.exit(app.exec())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.exception("Fatal error in main loop")
        sys.exit(1)
    finally:
        jarvis_speak("Goodbye, Sheriff.")


if __name__ == "__main__":
    main()
