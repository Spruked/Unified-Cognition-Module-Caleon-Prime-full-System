"""
Voice Processor for Unified Cognition Module
High-fidelity voice I/O using Cochlear Processor (Whisper) and Phonatory Output Module (Coqui TTS)
"""

import requests
import json
import time
import tempfile
import os
from typing import Optional, Dict, Any, List
import asyncio
import subprocess
import platform
import threading
import queue

# Import the sophisticated modules
COCHLEAR_AVAILABLE = False
try:
    # Add ISS_Module to path for cochlear processor dependencies
    import sys
    import os
    iss_path = os.path.join(os.path.dirname(__file__), 'ISS_Module')
    if iss_path not in sys.path:
        sys.path.insert(0, iss_path)

    # Try different import paths for cochlear processor
    try:
        from cochlear_processor_v2_0.transcribe import process_audio as cochlear_transcribe
        from cochlear_processor_v2_0.resonator_adapter import cochlear_to_resonator
        COCHLEAR_AVAILABLE = True
        print("[VOICE] Cochlear Processor v2.0 loaded successfully")
    except ImportError:
        # Try direct import from directory
        cochlear_path = os.path.join(os.path.dirname(__file__), 'cochlear_processor_v2.0')
        if cochlear_path not in sys.path:
            sys.path.insert(0, cochlear_path)
        try:
            from transcribe import process_audio as cochlear_transcribe
            from resonator_adapter import cochlear_to_resonator
            COCHLEAR_AVAILABLE = True
            print("[VOICE] Cochlear Processor v2.0 loaded successfully")
        except ImportError as e:
            print(f"[VOICE] Cochlear Processor v2.0 not available: {e}")
except Exception as e:
    print(f"[VOICE] Error loading Cochlear Processor: {e}")

class VoiceProcessor:
    def __init__(self):
        self.system = platform.system().lower()
        self.cerebral_cortex_url = "http://cerebral-cortex:8000"
        self.phonatory_url = "http://phonatory-output:8007"
        self.timeout = 30

        # Continuous listening state
        self.listening_active = False
        self.audio_queue = queue.Queue()
        self.listening_thread = None

        print(f"[VOICE] Initialized with Cochlear available: {COCHLEAR_AVAILABLE}")

    def get_module_status(self) -> Dict[str, Any]:
        """Get status of all voice processing modules"""
        status = {
            "cochlear_processor": {
                "available": COCHLEAR_AVAILABLE,
                "description": "Whisper-based speech recognition with prosody analysis",
                "status": "active" if COCHLEAR_AVAILABLE else "fallback_mode"
            },
            "phonatory_module": {
                "available": True,  # Assume HTTP service is available
                "description": "Coqui TTS with vocal tract simulation",
                "endpoint": self.phonatory_url
            },
            "cerebral_cortex": {
                "available": True,  # Assume HTTP service is available
                "description": "Cognitive processing and voice integration",
                "endpoint": self.cerebral_cortex_url
            }
        }

        # Test actual connectivity
        try:
            response = requests.get(f"{self.phonatory_url}/health", timeout=2)
            status["phonatory_module"]["http_status"] = response.status_code
        except:
            status["phonatory_module"]["http_status"] = "unreachable"

        try:
            response = requests.get(f"{self.cerebral_cortex_url}/health", timeout=2)
            status["cerebral_cortex"]["http_status"] = response.status_code
        except:
            status["cerebral_cortex"]["http_status"] = "unreachable"

        return status

    def speech_to_text(self, audio_file_path: Optional[str] = None, timeout: int = 10) -> Optional[str]:
        """Convert speech to text using Cochlear Processor (Whisper) or fallback"""
        try:
            print("[VOICE] Processing speech input...")

            # Use Cochlear Processor if available
            if COCHLEAR_AVAILABLE and audio_file_path:
                try:
                    print(f"[VOICE] Processing audio file: {audio_file_path}")

                    # Use cochlear processor for high-fidelity transcription
                    resonator_data = cochlear_to_resonator(audio_file_path)

                    # Send processed data to cerebral cortex
                    payload = {
                        "symbol": resonator_data.get("symbol", ""),
                        "confidence": resonator_data.get("confidence", 0.0),
                        "language": resonator_data.get("language", "unknown"),
                        "segments": resonator_data.get("segments", []),
                        "timbre": resonator_data.get("timbre", "speech"),
                        "processed_by": "cochlear_processor_v2"
                    }

                    # Send to cerebral cortex for processing
                    response = requests.post(f"{self.cerebral_cortex_url}/process_audio",
                                           json=payload, timeout=10)

                    if response.status_code == 200:
                        result = response.json()
                        transcribed_text = result.get("input_text", "")
                        print(f"[VOICE] Cochlear processed: '{transcribed_text}'")
                        return transcribed_text
                    else:
                        print(f"[VOICE] Cerebral cortex processing failed: {response.status_code}")

                except Exception as e:
                    print(f"[VOICE] Cochlear processing error: {e}")

            # Fallback: Record audio and process
            if not audio_file_path:
                audio_file_path = self._record_audio_segment(timeout)

            if audio_file_path and os.path.exists(audio_file_path):
                try:
                    # Try to use cochlear processor on recorded audio
                    if COCHLEAR_AVAILABLE:
                        resonator_data = cochlear_to_resonator(audio_file_path)
                        return resonator_data.get("symbol", "")
                    else:
                        # Basic fallback using system tools
                        return self._fallback_transcription(audio_file_path)
                finally:
                    # Clean up temporary file
                    try:
                        os.unlink(audio_file_path)
                    except:
                        pass

            print("[VOICE] No audio available for processing")
            return None

        except Exception as e:
            print(f"[VOICE] Speech-to-text error: {e}")
            return None

    def _record_audio_segment(self, duration: int = 5) -> Optional[str]:
        """Record a short audio segment for processing"""
        try:
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            temp_path = temp_file.name
            temp_file.close()

            print(f"[VOICE] Recording {duration} seconds of audio...")

            # Use system audio recording
            if self.system == "windows":
                # Use PowerShell to record audio (requires audio device)
                ps_cmd = f'powershell -Command "& {{\n$recorder = New-Object -ComObject WScript.Shell;\n$recorder.SendKeys(\'^%r\');\nStart-Sleep -Seconds {duration};\n$recorder.SendKeys(\'^%r\');\n}}"'
                # This is a placeholder - actual Windows audio recording would need different approach
                print("[VOICE] Windows audio recording not implemented - using placeholder")
                return None

            elif self.system == "linux":
                # Use arecord
                cmd = ["arecord", "-f", "cd", "-t", "wav", "-d", str(duration), temp_path]
                subprocess.run(cmd, capture_output=True, timeout=duration + 2)
                if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
                    return temp_path

            elif self.system == "darwin":  # macOS
                # Use sox or similar
                cmd = ["rec", temp_path, "trim", "0", str(duration)]
                subprocess.run(cmd, capture_output=True, timeout=duration + 2)
                if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
                    return temp_path

            print("[VOICE] Audio recording failed or no audio captured")
            return None

        except Exception as e:
            print(f"[VOICE] Audio recording error: {e}")
            return None

    def _fallback_transcription(self, audio_path: str) -> Optional[str]:
        """Basic fallback transcription when Cochlear is not available"""
        try:
            # Try using whisper directly if available
            try:
                import whisper
                model = whisper.load_model("base")
                result = model.transcribe(audio_path)
                return result["text"].strip()
            except ImportError:
                pass

            # Try using speech_recognition as last resort
            try:
                import speech_recognition as sr
                recognizer = sr.Recognizer()
                with sr.AudioFile(audio_path) as source:
                    audio = recognizer.record(source)
                    return recognizer.recognize_google(audio)
            except ImportError:
                pass
            except Exception as e:
                print(f"[VOICE] Fallback transcription failed: {e}")

            return None

        except Exception as e:
            print(f"[VOICE] Fallback transcription error: {e}")
            return None

    def text_to_speech(self, text: str, save_to_file: bool = False, filename: str = "output.wav") -> Optional[bytes]:
        """Convert text to speech using Phonatory Output Module (Coqui TTS)"""
        try:
            print(f"[VOICE] Synthesizing speech: {text[:50]}...")

            # Use Phonatory Output Module for high-fidelity speech synthesis
            payload = {
                "text": text,
                "pitch_factor": 1.0,
                "output_filename": filename if save_to_file else None
            }

            response = requests.post(f"{self.phonatory_url}/speak",
                                   json=payload,
                                   timeout=15)  # Longer timeout for synthesis

            if response.status_code == 200:
                result = response.json()
                print(f"[VOICE] Phonatory synthesis successful: {result.get('message', 'Success')}")

                # If save_to_file was requested, the file should be available at the path
                if save_to_file and result.get("output_path"):
                    print(f"[VOICE] Audio saved to: {result['output_path']}")

                return None  # Phonatory handles audio output directly

            else:
                print(f"[VOICE] Phonatory synthesis failed: {response.status_code} - {response.text}")
                return self._fallback_tts(text, save_to_file, filename)

        except requests.exceptions.RequestException as e:
            print(f"[VOICE] Phonatory module not available: {e}")
            return self._fallback_tts(text, save_to_file, filename)

        except Exception as e:
            print(f"[VOICE] Text-to-speech error: {e}")
            return self._fallback_tts(text, save_to_file, filename)

    def _fallback_tts(self, text: str, save_to_file: bool = False, filename: str = "output.wav") -> Optional[bytes]:
        """Fallback TTS using system capabilities when Phonatory is unavailable"""
        try:
            print(f"[VOICE] Using system TTS fallback")

            # Fallback to system TTS
            if self.system == "windows":
                # Use Windows PowerShell TTS
                try:
                    powershell_cmd = f'powershell -Command "Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak(\'{text.replace(chr(39), chr(39)+chr(39))}\')"'  # noqa
                    subprocess.run(powershell_cmd, shell=True, capture_output=True)
                    print("[VOICE] Windows TTS completed")
                except Exception as e:
                    print(f"[VOICE] Windows TTS failed: {e}")
                    print(f"[TTS] {text}")

            elif self.system == "linux":
                # Try espeak or other Linux TTS
                try:
                    subprocess.run(["espeak", text], capture_output=True)
                    print("[VOICE] Linux TTS completed")
                except FileNotFoundError:
                    print("[VOICE] espeak not available")
                    print(f"[TTS] {text}")
                except Exception as e:
                    print(f"[VOICE] Linux TTS failed: {e}")
                    print(f"[TTS] {text}")

            elif self.system == "darwin":  # macOS
                try:
                    subprocess.run(["say", text], capture_output=True)
                    print("[VOICE] macOS TTS completed")
                except Exception as e:
                    print(f"[VOICE] macOS TTS failed: {e}")
                    print(f"[TTS] {text}")

            else:
                print(f"[TTS] {text}")

            return None

        except Exception as e:
            print(f"[VOICE] Fallback TTS error: {e}")
            print(f"[TTS FALLBACK] {text}")
            return None

    def get_audio_devices(self) -> Dict[str, Any]:
        """Get information about available audio devices and processing modules"""
        try:
            devices = {
                "input_devices": ["System Default Microphone"],
                "output_devices": ["System Default Speakers"],
                "default_input": "System Default Microphone",
                "default_output": "System Default Speakers",
                "system": self.system,
                "cochlear_processor_available": COCHLEAR_AVAILABLE,
                "phonatory_module_available": True  # Assume available via HTTP
            }

            # Check actual audio devices if possible
            try:
                # Try to enumerate devices using pyaudio if available
                import pyaudio
                p = pyaudio.PyAudio()

                devices["input_devices"] = []
                devices["output_devices"] = []

                for i in range(p.get_device_count()):
                    device_info = p.get_device_info_by_index(i)
                    if device_info.get('maxInputChannels') > 0:
                        devices["input_devices"].append(f"Device {i}: {device_info.get('name', 'Unknown')}")
                    if device_info.get('maxOutputChannels') > 0:
                        devices["output_devices"].append(f"Device {i}: {device_info.get('name', 'Unknown')}")

                p.terminate()

                if devices["input_devices"]:
                    devices["default_input"] = devices["input_devices"][0]
                if devices["output_devices"]:
                    devices["default_output"] = devices["output_devices"][0]

            except ImportError:
                pass  # pyaudio not available
            except Exception as e:
                print(f"[VOICE] Error enumerating audio devices: {e}")

            # Set TTS/STT engine info
            if COCHLEAR_AVAILABLE:
                devices["stt_engine"] = "Cochlear Processor v2.0 (Whisper)"
            else:
                devices["stt_engine"] = "Fallback transcription"

            devices["tts_engine"] = "Phonatory Output Module (Coqui TTS)"

            return devices

        except Exception as e:
            print(f"[VOICE] Device enumeration error: {e}")
            return {"error": str(e)}

    def _continuous_listening_worker(self):
        """Background worker for continuous listening using Cochlear Processor"""
        print("[VOICE] Continuous listening worker started")

        while self.listening_active:
            try:
                # Record short audio segments for processing
                audio_path = self._record_audio_segment(duration=3)  # 3 second chunks

                if audio_path:
                    try:
                        # Process with Cochlear if available
                        if COCHLEAR_AVAILABLE:
                            resonator_data = cochlear_to_resonator(audio_path)
                            symbol = resonator_data.get("symbol", "").strip()

                            if symbol and len(symbol) > 0:
                                print(f"[VOICE] Detected speech: '{symbol}'")
                                self.audio_queue.put(symbol)
                        else:
                            # Fallback processing
                            text = self._fallback_transcription(audio_path)
                            if text and len(text.strip()) > 0:
                                print(f"[VOICE] Fallback detected: '{text}'")
                                self.audio_queue.put(text)

                    except Exception as e:
                        print(f"[VOICE] Continuous processing error: {e}")
                    finally:
                        # Clean up audio file
                        try:
                            os.unlink(audio_path)
                        except:
                            pass

                # Small delay between recordings
                time.sleep(0.5)

            except Exception as e:
                print(f"[VOICE] Continuous listening error: {e}")
                time.sleep(1)

        print("[VOICE] Continuous listening worker stopped")

    async def start_continuous_listening(self):
        """Start continuous voice listening with Cochlear Processor"""
        if self.listening_active:
            print("[VOICE] Continuous listening already active")
            return

        self.listening_active = True
        self.listening_thread = threading.Thread(target=self._continuous_listening_worker)
        self.listening_thread.daemon = True
        self.listening_thread.start()

        print("[VOICE] Continuous listening mode started")
        print("[VOICE] Using Cochlear Processor for speech recognition" if COCHLEAR_AVAILABLE else "[VOICE] Using fallback transcription")

    async def stop_continuous_listening(self):
        """Stop continuous voice listening"""
        if not self.listening_active:
            print("[VOICE] Continuous listening not active")
            return

        self.listening_active = False

        if self.listening_thread and self.listening_thread.is_alive():
            self.listening_thread.join(timeout=2)

        print("[VOICE] Continuous listening mode stopped")

    def get_queued_audio(self) -> Optional[str]:
        """Get the next recognized audio from the queue"""
        try:
            return self.audio_queue.get_nowait()
        except queue.Empty:
            return None

# Global instance
voice_processor = VoiceProcessor()