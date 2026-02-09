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
║              Zero-Cost AI Assistant | Hybrid Architecture                     ║
║                Local Client + Cloud Brain | Python 3.10+                      ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝

Entry point for JARVIS AI Assistant.
Orchestrates the Senses, Brain, Memory, and Hands.
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
    system_message,
    success_message,
    error_message,
    warning_message,
)
from src.core.exceptions import JarvisError

# Import Singletons
from src.senses import d_mic, d_stt, d_tts
from src.brain import d_brain
from src.memory import d_hippocampus
from src.tools import d_hands

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
    ║         [cyan]Zero-Cost AI Assistant v1.0.0[/cyan]                       ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
[/blue bold]
"""
    console.print(banner)


async def main_loop() -> None:
    """
    Main orchestration loop:
    Listen -> Wake Word -> Recall -> Think -> Act -> Speak -> Memorize
    """
    jarvis_speak("Ready for your command, Sheriff.")
    
    wake_word = settings.wake_word.lower()
    
    # Conversation State
    in_conversation = False
    last_interaction_time = 0
    conversation_timeout = 20.0  # Detailed commands take longer
    
    while True:
        try:
            # ─────────────────────────────────────────────────────────────
            # 1. LISTEN
            # ─────────────────────────────────────────────────────────────
            # audio_stream awaits voice activity
            audio_buffer = await d_mic.record_phrase()
            
            # Short-circuit if buffer is empty (too short/silence)
            if len(audio_buffer) < settings.audio_sample_rate * 0.5:
                # If in conversation and silence persists, check timeout
                if in_conversation and (asyncio.get_event_loop().time() - last_interaction_time > conversation_timeout):
                    in_conversation = False
                    console.print("[dim]Conversation timed out. Waiting for wake word.[/dim]")
                continue

            # ─────────────────────────────────────────────────────────────
            # 2. TRANSCRIBE (EARS)
            # ─────────────────────────────────────────────────────────────
            console.print(f"[dim]Audio captured. Length: {len(audio_buffer)} samples[/dim]")
            
            text = await d_stt.transcribe(audio_buffer)
            if not text:
                continue
            
            text_lower = text.lower()
            console.print(f"[bold green]Heard:[/bold green] '{text}'")

            # ─────────────────────────────────────────────────────────────
            # 3. WAKE WORD & CONVERSATIONAL LOGIC
            # ─────────────────────────────────────────────────────────────
            current_time = asyncio.get_event_loop().time()
            command = ""
            
            # Fuzzy Wake Word Detection (Whisper often mishears "Jarvis")
            wake_word_variants = [
                "jarvis", "darius", "jervis", "jarv", "jaravis", "jarvi", 
                "service", "harvest", "travis", "davis", "chavis"
            ]
            wake_detected = any(variant in text_lower for variant in wake_word_variants)
            
            # Case A: Explicit Wake Word
            if wake_detected:
                logger.info(f"Wake word detected in: '{text}'")
                
                # Speak Acknowledgment
                # No verbal acknowledgment - just listen for command
                
                # Extract Command (find which variant was used)
                for variant in wake_word_variants:
                    if variant in text_lower:
                        parts = text_lower.split(variant, 1)
                        command = parts[1].strip() if len(parts) > 1 else ""
                        break
                
                in_conversation = True
                last_interaction_time = current_time
                
                # If no command embedded with wake word, wait for it
                if not command:
                    console.print("[bold cyan]🎤 Listening for command...[/bold cyan]")
            
            # Case B: In Active Conversation (No Wake Word needed)
            elif in_conversation:
                # Optional: Filter out very short noise?
                if len(text) > 2: 
                    command = text
                    last_interaction_time = current_time
            
            # Processing
            if command:
                await process_interaction(command)
                # Reset conversation timer after replying
                last_interaction_time = asyncio.get_event_loop().time()
            elif in_conversation and not command:
                 # We heard text but couldn't parse a command? 
                 # Or maybe it was just background noise during conversation.
                 pass
            
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received in loop.")
            break
        except Exception as e:
            logger.error(f"Loop error: {e}", exc_info=True)
            await asyncio.sleep(0.1)  # Brief pause to prevent CPU spin on tight loop errors


async def process_interaction(user_input: str) -> None:
    """
    Process user command through the agentic brain.
    The brain handles all tool execution via function calling.
    """
    logger.info(f"Processing: {user_input}")

    # ─────────────────────────────────────────────────────────────
    # AGENTIC BRAIN (Handles thinking + tool execution)
    # ─────────────────────────────────────────────────────────────
    console.print("[bold blue]🧠 Processing...[/bold blue]")
    response = await d_brain.think(user_input)
    
    # Log and speak the response
    jarvis_speak(f"Reply: {response}")
    
    # Speak with interruption support
    # Speak (Blocking, no interruption)
    await d_tts.speak(response)
    d_hippocampus.memorize(f"User: {user_input} | JARVIS: {response[:100]}", "interaction")


def handle_shutdown(signum: int, frame) -> None:
    """Handle graceful shutdown."""
    console.print("\n")
    warning_message("Shutting down JARVIS...")
    # Clean up resources if needed
    sys.exit(0)


def main() -> None:
    """Main entry point."""
    # Signal Handlers
    signal.signal(signal.SIGINT, handle_shutdown)
    if sys.platform != "win32":
        signal.signal(signal.SIGTERM, handle_shutdown)
    
    print_banner()
    
    # Setup Logging
    setup_logging(level=settings.log_level)
    
    # Verify Config
    if not settings.active_llm_provider:
        error_message("No LLM API Key found! Please configure .env")
        sys.exit(1)
        
    success_message("All systems operational.")
    
    # Run Loop
    try:
        asyncio.run(main_loop())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.exception("Fatal error in main loop")
        sys.exit(1)
    finally:
        jarvis_speak("Goodbye, Sheriff.")


if __name__ == "__main__":
    main()
