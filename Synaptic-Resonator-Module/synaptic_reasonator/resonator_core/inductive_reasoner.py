#!/usr/bin/env python3
"""
inductive_reasoner.py
Minimal bottom-up (inductive) reasoner for CALI.

Observation-Pattern-Hypothesis cycle:
------------------------------------
1. observe(A("color","flamingo","pink"))
2. observe(A("color","flamingo","pink"))
3. observe(A("color","swan","white"))
4. kb.hypothesize()
→ [ color(X,Y) ⇒ probable_pattern('flamingo','pink',conf=1.0), ... ]

Differences from deductive_reasoner:
• Induction generalizes from observed facts (not predefined rules)
• Produces probabilistic hypotheses (support/confidence)
• Non-monotonic — new data can change prior conclusions
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple, Union, Iterator
from collections import defaultdict, Counter
import time

# ---------- Term & Atom ----------

@dataclass(frozen=True)
class V:
    """Logic variable (e.g., V('X'))."""
    name: str
    def __repr__(self) -> str:
        return f"?{self.name}"

@dataclass(frozen=True)
class A:
    """Predicate atom (e.g., A('color','flamingo','pink'))."""
    pred: str
    args: Tuple[Union[V, str, int, float], ...]
    def __init__(self, pred: str, *args: Union[V,str,int,float]):
        object.__setattr__(self, "pred", pred)
        object.__setattr__(self, "args", tuple(args))
    def __repr__(self) -> str:
        return f"{self.pred}({', '.join(map(str, self.args))})"

Term = Union[V,str,int,float]

# ---------- Inductive Knowledge Base ----------

class InductiveKB:
    """Observation-based knowledge base with pattern extraction."""
    def __init__(self) -> None:
        self._facts: List[A] = []
        self._counts: Counter[str] = Counter()
        self._pair_counts: Dict[str, Counter[Tuple]] = defaultdict(Counter)
        self._timestamp: float = time.time()

    # --- Ingest observations ---
    def observe(self, atom: A) -> None:
        """Record an observation (fact)."""
        self._facts.append(atom)
        key = atom.pred
        self._counts[key] += 1
        self._pair_counts[key][atom.args] += 1

    # --- Summaries ---
    def stats(self) -> Dict[str,int]:
        return dict(self._counts)

    # --- Pattern extraction ---
    def patterns(self, pred: str) -> List[Tuple[Tuple, int, float]]:
        """Return observed argument patterns with counts and confidence."""
        if pred not in self._pair_counts:
            return []
        total = sum(self._pair_counts[pred].values())
        results = []
        for args, n in self._pair_counts[pred].items():
            conf = round(n / total, 3)
            results.append((args, n, conf))
        results.sort(key=lambda x: -x[2])
        return results

    # --- Hypothesis generation ---
    def hypothesize(self, min_conf: float = 0.3) -> List[str]:
        """Generalize high-confidence patterns into probable rules."""
        hyps = []
        for pred, counts in self._pair_counts.items():
            total = sum(counts.values())
            for args, n in counts.items():
                conf = n / total
                if conf >= min_conf:
                    rule = f"{pred}({', '.join(map(str,args))}) :- observed {n}/{total} ({conf:.2f})."
                    hyps.append(rule)
        return hyps

    # --- Query ---
    def query(self, pred: str, arg_pos: int, value: str, min_conf: float = 0.3) -> List[Dict[str,Union[str,float]]]:
        """
        Given one argument, find probable completions.
        Example: query('color', 0, 'flamingo') → likely colors.
        """
        if pred not in self._pair_counts: return []
        total = sum(self._pair_counts[pred].values())
        results = []
        for args, n in self._pair_counts[pred].items():
            if len(args) <= arg_pos: continue
            if str(args[arg_pos]) == str(value):
                conf = n / total
                if conf >= min_conf:
                    results.append({
                        "pattern": args,
                        "support": n,
                        "confidence": round(conf,3)
                    })
        return sorted(results, key=lambda x: -x["confidence"])

# ---------- Example CLI ----------

if __name__ == "__main__":
    kb = InductiveKB()
    kb.observe(A("color","flamingo","pink"))
    kb.observe(A("color","flamingo","pink"))
    kb.observe(A("color","swan","white"))
    kb.observe(A("color","cardinal","red"))
    kb.observe(A("color","cardinal","red"))
    kb.observe(A("color","cardinal","red"))

    print(\"\\n--- Stats ---\")
    print(kb.stats())

    print(\"\\n--- Patterns(color) ---\")
    for p in kb.patterns(\"color\"): print(p)

    print(\"\\n--- Hypotheses ---\")
    for h in kb.hypothesize(): print(h)

    print(\"\\n--- Query: what colors are flamingos? ---\")
    for q in kb.query(\"color\",0,\"flamingo\"): print(q)
