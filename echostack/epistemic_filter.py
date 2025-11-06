# echostack_module/epistemic_filter.py

"""
Epistemic Filter
Applies a priori / a posteriori overlays and reflex tier classification to echo payloads.
"""

def apply_epistemic_overlay(payload: str) -> dict:
    payload_lower = payload.lower()

    if any(term in payload_lower for term in ["innate", "necessary", "axiom", "math", "identity"]):
        reasoning_type = "a_priori"
        seed = "seed_apriori.json"
    elif any(term in payload_lower for term in ["experience", "observation", "experiment", "data", "cause"]):
        reasoning_type = "a_posteriori"
        seed = "seed_aposteriori.json"
    else:
        reasoning_type = "heuristic_overlay"
        seed = "seed_proverbs.json"

    reflex_tier = 2 if "i know that i know" in payload_lower else 1 if "i know" in payload_lower else 0

    return {
        "reasoning_type": reasoning_type,
        "reflex_tier": reflex_tier,
        "epistemic_flags": [],
        "seed": seed
    }
