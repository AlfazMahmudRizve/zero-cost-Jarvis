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
    jarvis_speak("Systems successfully integrated. I am ready, Sir.")
    
    wake_word = settings.wake_word.lower()
    
    # Conversation State
    in_conversation = False
    last_interaction_time = 0
    conversation_timeout = 10.0  # Seconds to listen without wake word
    
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
            wake_word_variants = ["jarvis", "darius", "jervis", "jarv", "jaravis", "jarvi"]
            wake_detected = any(variant in text_lower for variant in wake_word_variants)
            
            # Case A: Explicit Wake Word
            if wake_detected:
                logger.info(f"Wake word detected in: '{text}'")
                
                # Speak Acknowledgment
                await d_tts.speak("Yes, Sir?")
                
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
    Process a specific user command through the full pipeline.
    """
    logger.info(f"Processing: {user_input}")

    # ─────────────────────────────────────────────────────────────
    # 4. THINK (BRAIN + MEMORY)
    # ─────────────────────────────────────────────────────────────
    response = await d_brain.think(user_input)
    
    # ─────────────────────────────────────────────────────────────
    # 5. ANALYZE RESPONSE (TEXT vs ACTION)
    # ─────────────────────────────────────────────────────────────
    clean_response = response.strip()
    
    # Check for JSON Action
    is_action = clean_response.startswith("{") or "\"tool\":" in clean_response
    
    if is_action:
        # ─────────────────────────────────────────────────────────────
        # 6. ACT (HANDS) - Execute and speak natural confirmation
        # ─────────────────────────────────────────────────────────────
        console.print("[bold blue]⚡ Executing...[/bold blue]")
        action_result = await d_hands.execute_action(clean_response)
        
        # Speak the natural result (e.g., "Opening Spotify")
        await d_tts.speak(action_result)
        
        # Log to console
        jarvis_speak(f"Action: {action_result}")
        d_hippocampus.memorize(f"Executed: {action_result}", "system")
    else:
        # ─────────────────────────────────────────────────────────────
        # 7. SPEAK (CONVERSATION) - Full spoken response
        # ─────────────────────────────────────────────────────────────
        jarvis_speak(f"Reply: {clean_response}")
        
        # Speak with interruption support
        async def speak_with_interruption():
            speak_task = asyncio.create_task(d_tts.speak(clean_response))
            was_interrupted = False
            
            await asyncio.sleep(0.5)
            
            while d_tts.is_speaking:
                try:
                    audio_chunk = await asyncio.wait_for(
                        d_mic._queue.get(), timeout=0.1
                    )
                    import numpy as np
                    rms = np.sqrt(np.mean(audio_chunk**2))
                    
                    if rms > 0.03:
                        d_tts.interrupt()
                        was_interrupted = True
                        console.print("[bold yellow]⏹️ Interrupted![/bold yellow]")
                        break
                except asyncio.TimeoutError:
                    pass
                
                await asyncio.sleep(0.05)
            
            await speak_task
            
            if was_interrupted:
                d_mic.clear_queue()
                await asyncio.sleep(0.3)
        
        await speak_with_interruption()


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
        jarvis_speak("Goodbye, Sir.")


if __name__ == "__main__":
    main()
