# phonatory_output_module.py
"""
Phonatory Output Module (POM)
Handles text-to-speech synthesis for Cognitive Caleon.
Provides the voice interface for articulated reasoning.
Uses gTTS (Google Text-to-Speech) for reliable container-based voice synthesis.
"""

import asyncio
import threading
import time
import tempfile
import os
from typing import Optional, Callable
from gtts import gTTS

try:
    import playsound
except ImportError:
    playsound = None
    print("Error: 'playsound' module not found. Install it with 'pip install playsound' for audio playback.")

class PhonatoryOutputModule:
    """
    Text-to-speech synthesis module.
    Converts text reasoning into audible speech output.
    Uses gTTS for high-quality, reliable voice synthesis in containers.
    """

    def __init__(self):
        self.speech_queue = asyncio.Queue()
        self.is_speaking = False
        self.speech_thread = None
        self.callbacks = []

        print("POM gTTS initialized successfully")

    def speak(self, text: str, async_mode: bool = True, callback: Optional[Callable] = None) -> bool:
        """
        Convert text to speech and speak it aloud using gTTS.

        Args:
            text: The text to speak
            async_mode: If True, speak asynchronously. If False, block until speech completes.
            callback: Optional callback function to call when speech completes

        Returns:
            bool: True if speech was initiated successfully
        """
        if not text or not text.strip():
            return False

        try:
            if async_mode:
                # Add to speech queue for async processing
                asyncio.create_task(self._queue_speech(text, callback))
                return True
            else:
                # Speak synchronously
                self._generate_and_play_speech(text)
                if callback:
                    callback()
                return True

        except Exception as e:
            print(f"POM speech synthesis error: {e}")
            return False

    async def _queue_speech(self, text: str, callback: Optional[Callable] = None):
        """Add speech to queue and process asynchronously"""
        await self.speech_queue.put((text, callback))

        # Start speech processing thread if not already running
        if not self.speech_thread or not self.speech_thread.is_alive():
            self.speech_thread = threading.Thread(target=self._process_speech_queue, daemon=True)
            self.speech_thread.start()

    def _process_speech_queue(self):
        """Process speech queue in background thread"""
        while True:
            try:
                # Get next speech item (blocking)
                text, callback = self.speech_queue.get(timeout=1)

                if text:
                    self.is_speaking = True
                    self._generate_and_play_speech(text)
                    self.is_speaking = False

                    if callback:
                        try:
                            callback()
                        except Exception as e:
                            print(f"POM speech callback error: {e}")

                self.speech_queue.task_done()

            except asyncio.QueueEmpty:
                continue
            except Exception as e:
                print(f"POM speech queue processing error: {e}")
                self.is_speaking = False

    def _generate_and_play_speech(self, text: str):
        """Generate speech using gTTS and play it"""
        try:
            # Create temporary MP3 file
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                temp_filename = temp_file.name

            # Generate speech using gTTS
            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(temp_filename)

            # Play the audio file
            if playsound:
                playsound.playsound(temp_filename, block=True)
            else:
                print(f"Cannot play sound: 'playsound' module is not available. File saved at {temp_filename}")

            # Clean up temp file after a delay
            def cleanup():
                time.sleep(1)  # Brief delay to ensure playback is complete
                try:
                    os.unlink(temp_filename)
                except:
                    pass

            cleanup_thread = threading.Thread(target=cleanup, daemon=True)
            cleanup_thread.start()

        except Exception as e:
            print(f"POM speech generation error: {e}")

    def stop_speech(self):
        """Stop current speech synthesis"""
        try:
            # Clear the speech queue
            while not self.speech_queue.empty():
                try:
                    self.speech_queue.get_nowait()
                    self.speech_queue.task_done()
                except:
                    break

            self.is_speaking = False

        except Exception as e:
            print(f"POM stop speech error: {e}")

    def get_speech_status(self) -> dict:
        """Get current speech synthesis status"""
        return {
            "is_speaking": self.is_speaking,
            "queue_size": self.speech_queue.qsize() if hasattr(self.speech_queue, 'qsize') else 0,
            "tts_available": True  # gTTS is always available if installed
        }

# Global instance
phonatory_output = PhonatoryOutputModule()

# Convenience function for direct use
def speak(text: str, async_mode: bool = True, callback: Optional[Callable] = None) -> bool:
    """
    Convenience function to speak text.
    This is the main interface used by other modules.
    """
    return phonatory_output.speak(text, async_mode, callback)