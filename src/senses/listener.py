"""
Listener Loop
Orchestrates the wake word detection and command listening.
"""

import asyncio
from src.core.config import settings
from src.core.logger import get_logger, jarvis_speak, system_message
from src.senses import d_mic, d_stt, d_tts

logger = get_logger(__name__)


class Listener:
    """
    Main audio loop:
    1. Listen for Wake Word ("Jarvis")
    2. Record Command
    3. Transcribe Command
    4. Execute (Placeholder)
    """

    def __init__(self):
        self.wake_word = settings.wake_word.lower()

    async def start(self):
        """Start the continuous listening loop."""
        jarvis_speak("Listening for wake word...")
        
        # Initial greeting
        # await d_tts.speak("Systems online. I am listening.")
        
        while True:
            try:
                # 1. Listen for audio (waits for Voice Activity)
                # logger.debug("Waiting for voice...")
                audio = await d_mic.record_phrase()
                
                # If audio is empty or too short, skip
                if len(audio) < settings.audio_sample_rate * 0.5:  # < 0.5s
                    continue

                # 2. Transcribe
                text = await d_stt.transcribe(audio)
                if not text:
                    continue
                    
                text_lower = text.lower()
                logger.debug(f"Heard: '{text}'")
                
                # 3. Check for Wake Word
                if self.wake_word in text_lower:
                    logger.info(f"Wake word detected: '{text}'")
                    
                    # Visual/Audio acknowledgement
                    # No verbal acknowledgment - handled in main.py
                    # await d_tts.speak("Yes?")
                    
                    # Extract command if present in the same phrase
                    # e.g., "Jarvis turn on the lights"
                    parts = text_lower.split(self.wake_word, 1)
                    command = parts[1].strip() if len(parts) > 1 else ""
                    
                    # If no command immediately following, listen again for the command
                    if not command:
                        # Short timeout listen for follow-up
                        jarvis_speak("Awaiting command...")
                        # await d_tts.speak("Ready.")
                        command_audio = await d_mic.record_phrase()
                        command = await d_stt.transcribe(command_audio)

                    if command:
                        await self.process_command(command)
                    else:
                        jarvis_speak("No command heard.")
                
                else:
                    # Ignore non-wake-word speech for now
                    # Or implement "conversation mode" logic later
                    pass

            except Exception as e:
                logger.error(f"Listener loop error: {e}", exc_info=True)
                await asyncio.sleep(1)

    async def process_command(self, command: str):
        """Process a recognized command."""
        logger.info(f"Processing command: {command}")
        jarvis_speak(f"Processing: {command}")
        
        # Send to Brain
        from src.brain import d_brain
        from src.tools import d_hands
        
        response = await d_brain.think(command)
        
        # Check if response is a JSON Action
        clean_response = response.strip()
        if clean_response.startswith("{") or clean_response.startswith("```json"):
            # Execute Action
            jarvis_speak("Executing action...")
            result_message = await d_hands.execute_action(clean_response)
            
            # Speak Confirmation
            jarvis_speak(f"Action: {result_message}")
            await d_tts.speak(result_message)
            
            # Memorize the result as well?
            # d_brain.memory.memorize(f"System Action Result: {result_message}", "system")
        else:
            # Standard Text Response
            jarvis_speak(f"Response: {response}")
            await d_tts.speak(response)


# Singleton instance
d_listener = Listener()
