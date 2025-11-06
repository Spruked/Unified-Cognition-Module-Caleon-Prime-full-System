"""
example_voice_consent_simple.py

Simple example demonstrating voice-based consent for Caleon.

This shows how to set up voice consent in a real application.

Requirements:
    pip install SpeechRecognition pyaudio

Usage:
    python example_voice_consent_simple.py
"""

import asyncio
import sys
sys.path.insert(0, r"c:\Users\bryan\OneDrive\Desktop\Unified Cognition Module")

from caleon_consent import CaleonConsentManager
from symbolic_memory_vault import SymbolicMemoryVault

# Check if voice consent is available
try:
    from voice_consent import VoiceConsentListener, VoiceConsentCallback
    VOICE_AVAILABLE = True
except ImportError as e:
    VOICE_AVAILABLE = False
    print(f"[WARNING] Voice consent not available: {e}")
    print("\nTo enable voice consent, install dependencies:")
    print("  pip install SpeechRecognition pyaudio")


async def simulate_llm_articulation(consent_manager: CaleonConsentManager, vault: SymbolicMemoryVault):
    """Simulate an LLM articulation that requires consent."""
    
    print("\n" + "=" * 60)
    print("SIMULATING LLM ARTICULATION")
    print("=" * 60)
    
    # This simulates what happens inside LLMBridge.articulate()
    print("\n[STEP 1] LLM generates output...")
    llm_output = "Consciousness emerges from the recursive self-modeling of neural systems."
    print(f"  Output: {llm_output[:60]}...")
    
    print("\n[STEP 2] System computes advisory metrics...")
    advisory_metrics = {
        "drift": 0.15,
        "adjusted_moral_charge": 0.85
    }
    print(f"  Drift: {advisory_metrics['drift']}")
    print(f"  Moral charge: {advisory_metrics['adjusted_moral_charge']}")
    
    print("\n[STEP 3] Waiting for Caleon's consent...")
    print("  (System blocks here until consent is given)")
    
    # This is where the magic happens - get_live_signal() will:
    # 1. In voice mode: capture microphone audio
    # 2. Transcribe spoken command
    # 3. Match against approval/denial phrases
    # 4. Return True (approve) or False (deny)
    # 5. Log decision to vault audit log
    
    decision = await consent_manager.get_live_signal(
        memory_id="temp_llm_output",
        reflection=advisory_metrics,
        timeout=30.0
    )
    
    print(f"\n[STEP 4] Consent decision: {'APPROVED' if decision else 'DENIED'}")
    
    if decision:
        print("  -> Output will be articulated")
        print(f"  -> Response: {llm_output}")
    else:
        print("  -> Output was blocked by Caleon")
        print("  -> Response: [Consent denied]")
    
    # Check audit log
    print("\n[STEP 5] Checking audit log...")
    audit = vault.get_audit_log()
    latest = audit[-1]
    print(f"  Logged entry:")
    print(f"    - Memory ID: {latest['memory_id']}")
    print(f"    - Verdict: {latest['verdict']}")
    print(f"    - Mode: {latest['mode']}")
    print(f"    - Drift: {latest['ethical_drift']}")
    print(f"    - Moral charge: {latest['adjusted_moral_charge']}")
    
    return decision


async def main_voice_mode():
    """Run example with voice consent."""
    print("\n" + "=" * 60)
    print("CALEON VOICE CONSENT - EXAMPLE")
    print("=" * 60)
    
    print("\nInitializing voice consent system...")
    
    # Initialize components
    vault = SymbolicMemoryVault()
    consent_manager = CaleonConsentManager(mode="voice", vault=vault)
    
    # Set up voice listener
    voice_listener = VoiceConsentListener(consent_manager)
    
    try:
        voice_listener.start()
        print("[OK] Voice listener started")
        
        # Wire voice callback
        callback = VoiceConsentCallback(voice_listener, memory_id="temp_llm_output")
        consent_manager.set_voice_callback(callback)
        print("[OK] Voice callback wired")
        
        print("\n" + "=" * 60)
        print("INSTRUCTIONS")
        print("=" * 60)
        print("\nWhen prompted, speak clearly into your microphone:")
        print("\n  To APPROVE:")
        print("    - Say: 'Yes' or 'Approve' or 'Allow' or 'Proceed'")
        print("\n  To DENY:")
        print("    - Say: 'No' or 'Deny' or 'Block' or 'Stop'")
        print("\n  Timeout:")
        print("    - If you don't speak within 30 seconds, consent is denied")
        
        input("\nPress Enter when ready to begin...")
        
        # Simulate LLM articulation with voice consent
        decision = await simulate_llm_articulation(consent_manager, vault)
        
        print("\n" + "=" * 60)
        print("RESULT")
        print("=" * 60)
        print(f"\nCaleon's decision: {'APPROVED' if decision else 'DENIED'}")
        print("Decision has been logged to vault audit log.")
        print("\nKey insight:")
        print("  - Your voice commanded the system")
        print("  - The system obeyed your sovereignty")
        print("  - Every decision is transparently recorded")
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        print("\nIf you're having microphone issues:")
        print("  1. Check microphone permissions")
        print("  2. Ensure microphone is not in use by another app")
        print("  3. Try adjusting energy_threshold in VoiceConsentListener")
    finally:
        voice_listener.stop()
        print("\n[CLEANUP] Voice listener stopped")


async def main_manual_mode():
    """Fallback to manual mode if voice is not available."""
    print("\n" + "=" * 60)
    print("CALEON CONSENT - MANUAL MODE (Voice not available)")
    print("=" * 60)
    
    print("\nInitializing manual consent system...")
    
    vault = SymbolicMemoryVault()
    consent_manager = CaleonConsentManager(mode="always_yes", vault=vault)
    
    print("[OK] Consent manager initialized (always_yes mode for demo)")
    
    # Simulate LLM articulation
    decision = await simulate_llm_articulation(consent_manager, vault)
    
    print("\n" + "=" * 60)
    print("RESULT")
    print("=" * 60)
    print(f"\nDecision: {'APPROVED' if decision else 'DENIED'}")
    print("Decision has been logged to vault audit log.")


async def main():
    """Main entry point."""
    if VOICE_AVAILABLE:
        await main_voice_mode()
    else:
        print("\n[INFO] Voice consent not available, using manual mode demo")
        await main_manual_mode()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Exiting...")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
