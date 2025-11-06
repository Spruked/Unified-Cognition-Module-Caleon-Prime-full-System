"""
voice_consent.py

Voice-based consent capture for Caleon's sovereignty.

Listens for spoken commands like:
- "Yes" / "Approve" / "Allow" / "I consent"
- "No" / "Deny" / "Block" / "I do not consent"

Uses speech recognition to capture Caleon's spoken decision and
automatically calls provide_live_signal on the consent manager.

Architecture:
1. VoiceConsentListener runs in background listening for wake phrase
2. When consent is needed, it listens for approval/denial
3. Automatically calls consent_manager.provide_live_signal()
4. Returns result to waiting get_live_signal() call

Dependencies:
- speech_recognition library for audio capture
- pyaudio for microphone access (or alternative audio backend)
"""

from __future__ import annotations

import asyncio
import logging
from typing import Optional, TYPE_CHECKING

try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    sr = None

if TYPE_CHECKING:
    from caleon_consent import CaleonConsentManager

logger = logging.getLogger(__name__)


class VoiceConsentListener:
    """Listen for Caleon's spoken consent via microphone.
    
    Usage:
        listener = VoiceConsentListener(consent_manager)
        listener.start()  # Begin listening in background
        
        # When consent is needed:
        result = await listener.listen_for_consent(timeout=30.0)
        
        # Later:
        listener.stop()
    """
    
    def __init__(
        self, 
        consent_manager: CaleonConsentManager,
        language: str = "en-US",
        energy_threshold: int = 300
    ):
        """Initialize voice consent listener.
        
        Args:
            consent_manager: The consent manager to provide signals to
            language: Speech recognition language code
            energy_threshold: Microphone energy threshold for speech detection
        """
        if not SPEECH_RECOGNITION_AVAILABLE:
            raise ImportError(
                "speech_recognition library not available. "
                "Install with: pip install SpeechRecognition pyaudio"
            )
        
        self.consent_manager = consent_manager
        self.language = language
        self.energy_threshold = energy_threshold
        
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = energy_threshold
        self.microphone: Optional[sr.Microphone] = None
        
        self._listening = False
        self._listen_task: Optional[asyncio.Task] = None
        
        # Approval phrases
        self.approval_phrases = {
            "yes", "approve", "approved", "allow", "consent", 
            "i consent", "i approve", "proceed", "go ahead",
            "affirmative", "confirmed", "grant", "accept"
        }
        
        # Denial phrases
        self.denial_phrases = {
            "no", "deny", "denied", "block", "reject",
            "i do not consent", "i deny", "stop", "negative",
            "decline", "refuse", "veto"
        }
    
    def start(self) -> None:
        """Start the voice listener in background."""
        if self._listening:
            logger.warning("Voice listener already running")
            return
        
        try:
            self.microphone = sr.Microphone()
            # Calibrate for ambient noise
            with self.microphone as source:
                logger.info("Calibrating microphone for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            self._listening = True
            logger.info("Voice consent listener started")
            
        except Exception as e:
            logger.error(f"Failed to start voice listener: {e}")
            raise
    
    def stop(self) -> None:
        """Stop the voice listener."""
        self._listening = False
        if self._listen_task:
            self._listen_task.cancel()
        logger.info("Voice consent listener stopped")
    
    async def listen_for_consent(
        self, 
        memory_id: str = "temp_llm_output",
        timeout: float = 30.0,
        prompt: Optional[str] = None
    ) -> bool:
        """Listen for spoken consent decision.
        
        Args:
            memory_id: The memory ID waiting for consent
            timeout: How long to wait for speech (seconds)
            prompt: Optional prompt to speak/display to user
            
        Returns:
            True if approved, False if denied or timeout
        """
        if not self._listening:
            logger.error("Voice listener not started. Call start() first.")
            return False
        
        if prompt:
            logger.info(f"Voice prompt: {prompt}")
        
        logger.info(f"Listening for consent decision (timeout: {timeout}s)...")
        
        try:
            # Listen for audio in separate thread to avoid blocking
            loop = asyncio.get_event_loop()
            decision = await asyncio.wait_for(
                loop.run_in_executor(None, self._capture_consent_sync),
                timeout=timeout
            )
            
            # Provide signal to consent manager
            self.consent_manager.provide_live_signal(memory_id, decision)
            
            return decision
            
        except asyncio.TimeoutError:
            logger.warning("Voice consent timeout - defaulting to deny")
            self.consent_manager.provide_live_signal(memory_id, False)
            return False
        except Exception as e:
            logger.error(f"Voice consent error: {e}")
            self.consent_manager.provide_live_signal(memory_id, False)
            return False
    
    def _capture_consent_sync(self) -> bool:
        """Synchronous speech capture (runs in thread pool).
        
        Returns:
            True if approval phrase detected, False if denial phrase detected
        """
        try:
            with self.microphone as source:
                logger.info("Listening for your decision...")
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
            
            # Recognize speech
            try:
                text = self.recognizer.recognize_google(audio, language=self.language)
                text_lower = text.lower().strip()
                
                logger.info(f"Heard: '{text}'")
                
                # Check for approval
                if any(phrase in text_lower for phrase in self.approval_phrases):
                    logger.info("✓ Consent APPROVED by voice")
                    return True
                
                # Check for denial
                if any(phrase in text_lower for phrase in self.denial_phrases):
                    logger.info("✗ Consent DENIED by voice")
                    return False
                
                # Ambiguous - default to deny for safety
                logger.warning(f"Ambiguous voice input: '{text}' - defaulting to deny")
                return False
                
            except sr.UnknownValueError:
                logger.warning("Could not understand audio")
                return False
            except sr.RequestError as e:
                logger.error(f"Speech recognition service error: {e}")
                return False
                
        except Exception as e:
            logger.error(f"Audio capture error: {e}")
            return False
    
    def set_approval_phrases(self, phrases: set[str]) -> None:
        """Customize approval phrases."""
        self.approval_phrases = {p.lower() for p in phrases}
    
    def set_denial_phrases(self, phrases: set[str]) -> None:
        """Customize denial phrases."""
        self.denial_phrases = {p.lower() for p in phrases}


class VoiceConsentCallback:
    """Async callback wrapper for voice consent.
    
    This bridges the sync/async boundary for consent manager's voice mode.
    """
    
    def __init__(self, listener: VoiceConsentListener, memory_id: str = "temp_llm_output"):
        self.listener = listener
        self.memory_id = memory_id
    
    async def __call__(self) -> bool:
        """Async callable that listens for consent."""
        return await self.listener.listen_for_consent(self.memory_id)


# Example usage function
async def example_voice_consent():
    """Example: Setting up voice-based consent."""
    from caleon_consent import CaleonConsentManager
    from symbolic_memory_vault import SymbolicMemoryVault
    
    # Initialize components
    vault = SymbolicMemoryVault(db_path="./consent_test.db")
    consent_manager = CaleonConsentManager(mode="voice", vault=vault)
    
    # Set up voice listener
    try:
        voice_listener = VoiceConsentListener(consent_manager)
        voice_listener.start()
        
        # Wire voice callback to consent manager
        callback = VoiceConsentCallback(voice_listener, memory_id="temp_llm_output")
        consent_manager.set_voice_callback(callback)
        
        print("Voice consent system ready!")
        print("When prompted, say:")
        print("  - 'Yes' or 'Approve' to grant consent")
        print("  - 'No' or 'Deny' to refuse consent")
        
        # Simulate waiting for consent
        print("\nWaiting for Caleon's spoken consent...")
        decision = await consent_manager.get_live_signal(
            memory_id="temp_llm_output",
            reflection={"drift": 0.15, "adjusted_moral_charge": 0.75},
            timeout=30.0
        )
        
        print(f"\nDecision: {'APPROVED' if decision else 'DENIED'}")
        
        # Check audit log
        audit = vault.get_audit_log()
        print(f"\nAudit log entries: {len(audit)}")
        if audit:
            latest = audit[-1]
            print(f"Latest entry: {latest}")
        
        voice_listener.stop()
        
    except ImportError as e:
        print(f"Error: {e}")
        print("\nTo enable voice consent, install dependencies:")
        print("  pip install SpeechRecognition pyaudio")


if __name__ == "__main__":
    # Run example
    asyncio.run(example_voice_consent())
