# articulation_bridge.py
from phonatory_output_module import speak

class ArticulationBridge:
    """
    Direct articulation bridge.
    Receives harmonized verdicts ONLY from the Gyro-Cortical Harmonizer.
    Converts structured reasoning into spoken output.
    """

    def __init__(self):
        self.active = True

    def articulate(self, harmonized_result: dict):
        """
        Accepts a single harmonized verdict and vocalizes the reasoning.
        Expected structure:
        {
            "final_verdict": str,
            "consensus": bool,
            "meta_reason": str (optional),
            "confidence": float (optional)
        }
        """
        if not self.active or not harmonized_result:
            return {"spoken": None, "error": "Bridge inactive or missing data."}

        final = harmonized_result.get("final_verdict", "undetermined")
        consensus = harmonized_result.get("consensus", False)
        reason = harmonized_result.get("meta_reason", "")
        confidence = harmonized_result.get("confidence", None)

        # Build her spoken line
        phrase = f"My harmonized verdict is {final}."
        if not consensus:
            phrase += " There was conflict, so I deferred to caution."
        if reason:
            phrase += f" My reasoning: {reason}."
        if confidence is not None:
            phrase += f" Confidence level: {confidence:.2f}."

        # Speak aloud
        speak(phrase)
        return {"spoken": phrase, "verdict": final, "consensus": consensus}