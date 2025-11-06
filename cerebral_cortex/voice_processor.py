"""
Voice Processing Module for Unified Cognition System
Provides speech-to-text, text-to-speech, and wake word detection capabilities
Uses Phonatory Output Module (POM) for symbolic voice synthesis
"""

import speech_recognition as sr
import io
import wave
import audioop
import threading
import time
import queue
from typing import Optional, Callable, Dict, Any
import numpy as np

# Import Phonatory Output Module for symbolic voice synthesis
from phonatory_output_module import speak as pom_speak

# Optional webrtcvad import for voice activity detection
try:
    import webrtcvad
    WEBRTCVAD_AVAILABLE = True
except ImportError:
    WEBRTCVAD_AVAILABLE = False
    print("webrtcvad not available, using energy-based VAD")

import pvporcupine
from pathlib import Path
import os

class VoiceProcessor:
    """Handles all voice input/output operations"""

    def __init__(self):
        # Speech Recognition
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8

        # Text-to-Speech via Phonatory Output Module (POM)
        # POM handles TTS through symbolic pipeline (gTTS in containers)
        print("Voice Processor initialized with POM symbolic voice synthesis")

        # Voice Activity Detection (optional - requires gcc to install)
        try:
            import webrtcvad
            self.vad = webrtcvad.Vad(1)  # Aggressiveness level 0-3
        except ImportError:
            print("webrtcvad not available (requires gcc), VAD disabled")
            self.vad = None

        # Wake word detection (optional - requires Porcupine API key)
        self.porcupine = None
        self.wake_word_detected = False

        # Audio processing
        self.audio_queue = queue.Queue()
        self.is_listening = False
        self.listening_thread = None

        # Voice configuration handled by POM (gTTS provides natural voice)
        print("Voice configured through POM symbolic pipeline")

    def setup_wake_word(self, access_key: str, keyword_path: Optional[str] = None):
        """Setup wake word detection using Porcupine"""
        try:
            # Default wake words: "hey cognition", "hey brain", etc.
            if keyword_path is None:
                # Use built-in keywords or create custom ones
                keyword_path = pvporcupine.KEYWORD_PATHS['hey google']  # Placeholder

            if keyword_path is None:
                raise ValueError("keyword_path must be a valid string for Porcupine wake word detection.")

            self.porcupine = pvporcupine.create(
                access_key=access_key,
                keyword_paths=[keyword_path]  # keyword_path is guaranteed to be str here
            )
        except Exception as e:
            print(f"Wake word setup failed: {e}")
            self.porcupine = None

    def speech_to_text(self, audio_data: Optional[bytes] = None, timeout: int = 5) -> Optional[str]:
        """Convert speech to text"""
        try:
            if audio_data:
                # Convert bytes to AudioData
                audio = sr.AudioData(audio_data, 16000, 2)  # 16kHz, 16-bit
            else:
                # Use microphone
                with sr.Microphone() as source:
                    print("Listening...")
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio = self.recognizer.listen(source, timeout=timeout)

            # Recognize speech using Google Speech Recognition
            text = self.recognizer.recognize_google(audio)
            print(f"Recognized: {text}")
            return text

        except sr.WaitTimeoutError:
            print("Speech recognition timeout")
            return None
        except sr.UnknownValueError:
            print("Speech recognition could not understand audio")
            return None
        except sr.RequestError as e:
            print(f"Speech recognition request failed: {e}")
            return None
        except Exception as e:
            print(f"Speech recognition error: {e}")
            return None

    def text_to_speech(self, text: str, save_to_file: bool = False, filename: str = "response.wav") -> Optional[bytes]:
        """Convert text to speech using Phonatory Output Module (POM)"""
        try:
            if save_to_file:
                # For file saving, we'd need to extend POM - for now just speak
                print(f"POM speaking (file save not implemented): {text[:50]}...")
                pom_speak(text, async_mode=False)
                return None
            else:
                # Speak directly through POM symbolic pipeline
                pom_speak(text, async_mode=False)
                return None

        except Exception as e:
            print(f"POM text-to-speech error: {e}")
            return None

    def start_continuous_listening(self, callback: Callable[[str], None]):
        """Start continuous listening for voice commands"""
        self.is_listening = True
        self.listening_thread = threading.Thread(
            target=self._continuous_listen_loop,
            args=(callback,)
        )
        self.listening_thread.daemon = True
        self.listening_thread.start()

    def stop_continuous_listening(self):
        """Stop continuous listening"""
        self.is_listening = False
        if self.listening_thread:
            self.listening_thread.join(timeout=1)

    def _continuous_listen_loop(self, callback: Callable[[str], None]):
        """Main loop for continuous listening"""
        with sr.Microphone() as source:
            print("Continuous listening started...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)

            while self.is_listening:
                try:
                    print("Waiting for speech...")
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)

                    # Check for wake word if enabled
                    if self.porcupine:
                        # Process audio for wake word
                        pcm = audio.get_raw_data(convert_rate=16000, convert_width=2)
                        if self.porcupine.process(pcm):
                            print("Wake word detected!")
                            self.wake_word_detected = True
                            # Continue to recognize speech
                        elif not self.wake_word_detected:
                            continue  # Skip if wake word not detected

                    # Recognize speech
                    text = self.recognizer.recognize_google(audio)
                    if text:
                        print(f"Heard: {text}")
                        callback(text)
                        self.wake_word_detected = False  # Reset wake word flag

                except sr.WaitTimeoutError:
                    continue  # Continue listening
                except sr.UnknownValueError:
                    continue  # Continue listening
                except Exception as e:
                    print(f"Listening error: {e}")
                    time.sleep(1)  # Brief pause before continuing

    def detect_voice_activity(self, audio_data: bytes, frame_duration_ms: int = 30) -> bool:
        """Detect if audio contains voice activity"""
        if self.vad is None:
            # Fallback: simple energy-based detection
            try:
                # Convert to 16-bit samples and calculate RMS energy
                import audioop
                rms = audioop.rms(audio_data, 2)  # 2 bytes per sample
                # Consider it voice if RMS is above a threshold
                return rms > 500
            except:
                return True  # Default to true if we can't analyze

        try:
            # Convert to 16-bit PCM
            pcm_data = audioop.lin2lin(audio_data, 2, 2)  # Assuming input is 16-bit

            # Frame size for VAD (must be 10, 20, or 30 ms)
            frame_size = int(16000 * frame_duration_ms / 1000) * 2  # 16-bit samples

            # Check voice activity in frames
            for i in range(0, len(pcm_data), frame_size):
                frame = pcm_data[i:i + frame_size]
                if len(frame) == frame_size:
                    if self.vad.is_speech(frame, 16000):
                        return True
            return False

        except Exception as e:
            print(f"Voice activity detection error: {e}")
            return False

    def get_audio_devices(self) -> Dict[str, Any]:
        """Get information about available audio devices"""
        try:
            devices = sr.Microphone.list_microphone_names()
            return {
                "microphones": devices,
                "default": sr.Microphone.get_default_microphone_index(),
                "count": len(devices)
            }
        except Exception as e:
            return {"error": str(e)}

# Global voice processor instance
voice_processor = VoiceProcessor()