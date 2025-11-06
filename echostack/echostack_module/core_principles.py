# echostack_module/core_principles.py

"""
Core Principles Module
Defines foundational logic principles used across EchoStack modules.
"""

CORE_PRINCIPLES = {
    "simplest_sufficient_cause": {
        "definition": "Prefer the explanation that requires the fewest assumptions while still accounting for all observed phenomena.",
        "source": "seed_ockhams_filter.json",
        "tier": "logic_filter"
    },
    "non_redundant_logic": {
        "definition": "Eliminate steps that do not contribute to the outcome or introduce unnecessary complexity.",
        "source": "seed_ockhams_filter.json",
        "tier": "logic_filter"
    },
    "minimal_viable_inference": {
        "definition": "Select the smallest set of premises that still yield the intended conclusion.",
        "source": "seed_ockhams_filter.json",
        "tier": "logic_filter"
    },
    "law_of_identity": {
        "definition": "Every object is identical to itself; A is A.",
        "source": "seed_apriori.json",
        "tier": "foundational_logic"
    },
    "law_of_non_contradiction": {
        "definition": "No statement can be both true and false at the same time and in the same respect.",
        "source": "seed_apriori.json",
        "tier": "foundational_logic"
    },
    "law_of_excluded_middle": {
        "definition": "For any proposition, either that proposition is true, or its negation is true.",
        "source": "seed_apriori.json",
        "tier": "foundational_logic"
    },
    "synthetic_a_priori": {
        "definition": "Judgments that are both informative and known independently of experience.",
        "source": "seed_apriori.json",
        "tier": "epistemological_structure"
    }
}

def get_principle(term: str) -> dict:
    return CORE_PRINCIPLES.get(term.lower(), {"error": "Principle not found"})

def get_core_principles() -> dict:
    """Get all core principles"""
    return CORE_PRINCIPLES
