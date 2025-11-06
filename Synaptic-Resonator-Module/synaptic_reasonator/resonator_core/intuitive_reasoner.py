#!/usr/bin/env python3
"""
intuitive_reasoner.py
CALI — Intuitive (System 1) Reasoner
====================================
Fast, associative, emotion-weighted reasoning engine.

It models unconscious, heuristic judgment based on prior experience.
Where inductive reasoning builds patterns deliberately, this module
retrieves and weighs associations instantly — a computational analogy
of intuition.

Key Principles:
---------------
• System 1 thinking (fast, automatic)
• Weighted by emotion, recency, and frequency
• Produces probable, not guaranteed, judgments

Example
-------
from intuitive_reasoner import IntuitiveKB, A

kb = IntuitiveKB()
kb.observe(A("situation","dark_alley"), emotion=-0.8)
kb.observe(A("response","avoid"), emotion=0.7)
kb.observe(A("situation","friend_smiles"), emotion=0.9)
kb.observe(A("response","approach"), emotion=0.8)

print("\\nSnap judgment for 'dark_alley':")
print(kb.snap_judgment("dark_alley"))
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple, Union
from collections import defaultdict, deque, Counter
import math
import time

# ---------- Term & Atom ----------

@dataclass(frozen=True)
class V:
    """Logic variable."""
    name: str
    def __repr__(self) -> str:
        return f"?{self.name}"

@dataclass(frozen=True)
class A:
    """Predicate atom (e.g., A('situation','storm'))."""
    pred: str
    args: Tuple[Union[V,str,int,float], ...]
    def __init__(self, pred: str, *args: Union[V,str,int,float]):
        object.__setattr__(self, "pred", pred)
        object.__setattr__(self, "args", tuple(args))
    def __repr__(self) -> str:
        return f"{self.pred}({', '.join(map(str,self.args))})"

Term = Union[V,str,int,float]

# ---------- Intuitive Knowledge Base ----------

class IntuitiveKB:
    """
    Experience memory for associative, emotion-weighted reasoning.
    Each observation carries affect (emotion), recency, and frequency.
    """
    def __init__(self, max_memory:int=500):
        self.memory = deque(maxlen=max_memory)
        self.freq_counter = Counter()
        self.affect_map: Dict[str, float] = defaultdict(float)
        self.timestamp_map: Dict[str, float] = {}
        self.start_time = time.time()

    # --- Observation ---
    def observe(self, atom:A, emotion:float=0.0):
        """
        Store an experience atom with emotional weight.
        emotion ∈ [-1,1]; negative=avoidance, positive=attraction
        """
        key = f"{atom.pred}:{atom.args}"
        self.memory.append(key)
        self.freq_counter[key] += 1
        self.affect_map[key] += emotion
        self.timestamp_map[key] = time.time()

    # --- Association ---
    def associate(self, term:str, top_n:int=3) -> List[Tuple[str,float]]:
        """
        Find top-n associative matches by frequency and co-occurrence proximity.
        """
        matches = []
        for k,v in self.freq_counter.items():
            if term in k:
                affect = self.affect_map[k]
                age = max(1.0, time.time()-self.timestamp_map.get(k,self.start_time))
                recency = 1/(1+math.log(age))
                score = (v * recency) + affect
                matches.append((k,round(score,3)))
        matches.sort(key=lambda x: -x[1])
        return matches[:top_n]

    # --- Heuristic computation ---
    def heuristic_strength(self, key:str) -> float:
        f = self.freq_counter.get(key,0)
        a = self.affect_map.get(key,0.0)
        age = max(1.0, time.time()-self.timestamp_map.get(key,self.start_time))
        rec = 1/(1+math.log(age))
        return round((f*0.5 + a*5 + rec*2)/10,3)

    # --- Snap Judgment ---
    def snap_judgment(self, cue:str) -> Dict[str,Union[str,float]]:
        """
        Return immediate 'gut' decision for a given cue term.
        Combines association strength, emotion, and recency.
        """
        if not self.memory:
            return {"decision":"unknown","confidence":0.0}
        best=None; best_score=-999
        for k in self.freq_counter:
            if cue in k:
                score=self.heuristic_strength(k)
                if score>best_score:
                    best_score=score; best=k
        if best is None:
            return {"decision":"unclear","confidence":0.0}
        return {"decision":best,"confidence":round(best_score,3)}

    # --- Emotional profile ---
    def affect_profile(self) -> Dict[str,float]:
        total=sum(abs(v) for v in self.affect_map.values()) or 1
        return {k:round(v/total,3) for k,v in self.affect_map.items()}

# ---------- CLI Example ----------

if __name__ == "__main__":
    kb = IntuitiveKB()
    kb.observe(A("situation","dark_alley"), emotion=-0.8)
    kb.observe(A("response","avoid"), emotion=0.7)
    kb.observe(A("situation","friend_smiles"), emotion=0.9)
    kb.observe(A("response","approach"), emotion=0.8)
    kb.observe(A("situation","storm_clouds"), emotion=-0.5)
    kb.observe(A("response","seek_shelter"), emotion=0.6)

    print(\"\\n--- ASSOCIATIONS for 'dark' ---\")
    print(kb.associate(\"dark\"))

    print(\"\\n--- SNAP JUDGMENT ---\")
    print(kb.snap_judgment(\"dark\"))

    print(\"\\n--- AFFECT PROFILE ---\")
    for k,v in kb.affect_profile().items(): print(k,v)
