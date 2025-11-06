#!/usr/bin/env python3
"""
deductive_reasoner.py
Minimal Horn-clause reasoner for CALI.

• Facts:   parent("alice","bob")
• Rules:   ancestor(X,Y) :- parent(X,Y).
           ancestor(X,Y) :- parent(X,Z), ancestor(Z,Y).

API (quick start)
-----------------
from deductive_reasoner import KB, V, A

kb = KB()
kb.fact(A("parent", "alice", "bob"))
kb.fact(A("parent", "bob", "carol"))
kb.rule(A("ancestor", V("X"), V("Y")), [A("parent", V("X"), V("Y"))])
kb.rule(A("ancestor", V("X"), V("Y")), [A("parent", V("X"), V("Z")), A("ancestor", V("Z"), V("Y"))])

for sol in kb.query(A("ancestor", "alice", V("Who")), max_solutions=5):
    print(sol)  # {'Who': 'bob'} then {'Who': 'carol'}

Notes
-----
• Deterministic, no network, pure Python.
• Backward chaining with occurs-check and variable standardization-apart.
• Safe guards: max_depth, max_solutions.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Iterable, Iterator, List, Optional, Tuple, Union
import itertools
import time
import re

# ---------- Term & Atom ----------

@dataclass(frozen=True)
class V:
    """Logic variable (e.g., V('X'))."""
    name: str
    def __repr__(self) -> str:
        return f"?{self.name}"

@dataclass(frozen=True)
class A:
    """Predicate atom: A('parent', 'alice', 'bob') or A('p', V('X'))."""
    pred: str
    *args: Tuple[Union['V', str, int, float], ...]  # type: ignore

    def __init__(self, pred: str, *args: Union[V, str, int, float]) -> None:
        object.__setattr__(self, "pred", pred)
        object.__setattr__(self, "args", tuple(args))

    def __repr__(self) -> str:
        return f"{self.pred}({', '.join(map(str, self.args))})"

Term = Union[V, str, int, float]
Subst = Dict[V, Term]

# ---------- Utilities ----------

_gensym_counter = itertools.count(1)

def _gensym(prefix: str = "_") -> str:
    return f"{prefix}{next(_gensym_counter)}"

def _is_var(x: Term) -> bool:
    return isinstance(x, V)

def _walk(x: Term, s: Subst) -> Term:
    """Chase substitutions until fixed-point."""
    while _is_var(x) and x in s:
        x = s[x]
    return x

def _occurs(v: V, x: Term, s: Subst) -> bool:
    """Occurs-check: prevent X = f(X)."""
    x = _walk(x, s)
    if v == x:
        return True
    if isinstance(x, A):
        return any(_occurs(v, a, s) for a in x.args)
    return False

def _extend(s: Subst, v: V, x: Term) -> Optional[Subst]:
    if _occurs(v, x, s):
        return None
    s2 = dict(s)
    s2[v] = x
    return s2

def unify(x: Union[Term, A], y: Union[Term, A], s: Optional[Subst]) -> Optional[Subst]:
    """Robinson unification with occurs-check."""
    if s is None:
        return None
    x = _walk(x, s)  # type: ignore[arg-type]
    y = _walk(y, s)  # type: ignore[arg-type]
    if x == y:
        return s
    if _is_var(x):  # type: ignore[arg-type]
        return _extend(s, x, y)  # type: ignore[arg-type]
    if _is_var(y):  # type: ignore[arg-type]
        return _extend(s, y, x)  # type: ignore[arg-type]
    if isinstance(x, A) and isinstance(y, A):
        if x.pred != y.pred or len(x.args) != len(y.args):
            return None
        for xa, ya in zip(x.args, y.args):
            s = unify(xa, ya, s)
            if s is None:
                return None
        return s
    return None

def apply(s: Subst, x: Union[Term, A]) -> Union[Term, A]:
    """Deep apply substitution to a term/atom."""
    x = _walk(x, s)  # type: ignore[arg-type]
    if isinstance(x, A):
        return A(x.pred, *[apply(s, a) for a in x.args])  # type: ignore[arg-type]
    return x  # type: ignore[return-value]

# ---------- Rules & KB ----------

@dataclass(frozen=True)
class Rule:
    head: A
    body: Tuple[A, ...]  # empty body == fact

    def __repr__(self) -> str:
        return f"{self.head} :- {', '.join(map(str, self.body)) or 'true'}."

def _std_apart(rule: Rule) -> Rule:
    """Standardize variables apart per application to avoid name capture."""
    mapping: Dict[V, V] = {}
    def rename_term(t: Term) -> Term:
        if isinstance(t, V):
            if t not in mapping:
                mapping[t] = V(f"{t.name}_{_gensym()}")
            return mapping[t]
        return t
    def rename_atom(atom: A) -> A:
        return A(atom.pred, *[rename_term(a) for a in atom.args])
    return Rule(rename_atom(rule.head), tuple(rename_atom(b) for b in rule.body))

class KB:
    """Knowledge base with naive predicate index."""
    def __init__(self) -> None:
        self._rules: List[Rule] = []
        self._index: Dict[str, List[int]] = {}

    # Ingestion
    def fact(self, atom: A) -> None:
        self.rule(atom, [])  # fact is a rule with empty body

    def rule(self, head: A, body: Iterable[A]) -> None:
        r = Rule(head=head, body=tuple(body))
        idx = len(self._rules)
        self._rules.append(r)
        self._index.setdefault(head.pred, []).append(idx)

    # Query
    def query(
        self,
        goal: A,
        *,
        max_depth: int = 32,
        max_solutions: int = 50,
        timeout_s: float = 5.0,
    ) -> Iterator[Dict[str, Term]]:
        """
        Backward-chaining query generator.
        Yields dicts mapping variable names to ground terms.
        """
        start = time.time()
        solutions = 0
        goal0 = goal

        def bc_and(goals: List[A], s: Subst, depth: int) -> Iterator[Subst]:
            nonlocal solutions
            if s is None:
                return
            if time.time() - start > timeout_s:
                return
            if depth > max_depth:
                return
            if not goals:
                yield s
                return
            first, rest = goals[0], goals[1:]
            yield from bc_or(first, rest, s, depth)

        def bc_or(goal_atom: A, rest_goals: List[A], s: Subst, depth: int) -> Iterator[Subst]:
            # Try each rule whose head predicate matches
            for idx in self._index.get(goal_atom.pred, []):
                rule = _std_apart(self._rules[idx])
                s2 = unify(rule.head, goal_atom, dict(s))
                if s2 is None:
                    continue
                new_goals = list(rule.body) + rest_goals
                yield from bc_and(new_goals, s2, depth + 1)

        # Kick off
        for s in bc_and([goal0], {}, 0):
            out: Dict[str, Term] = {}
            for arg in goal0.args:
                if isinstance(arg, V):
                    val = apply(s, arg)
                    if isinstance(val, V):
                        # Unbound; skip
                        continue
                    out[arg.name] = val  # ground
            # Also expose any other bound variables
            for v, val in s.items():
                if isinstance(v, V) and v.name not in out and not isinstance(val, V):
                    out[v.name] = val
            yield out
            solutions += 1
            if solutions >= max_solutions:
                break

# ---------- Pretty helpers ----------

def ground(atom: A, subst: Subst) -> A:
    """Return grounded version of an atom under a substitution."""
    return apply(subst, atom)  # type: ignore[return-value]

def parse_var(s: str) -> V:
    """
    Convenience: parse '?X' or 'X' to V('X').
    """
    name = s[1:] if s.startswith("?") else s
    return V(name)

# ---------- CLI demo ----------

if __name__ == "__main__":
    # Example KB: family relations
    kb = KB()
    kb.fact(A("parent", "alice", "bob"))
    kb.fact(A("parent", "bob", "carol"))
    kb.rule(A("ancestor", V("X"), V("Y")), [A("parent", V("X"), V("Y"))])
    kb.rule(A("ancestor", V("X"), V("Y")), [A("parent", V("X"), V("Z")), A("ancestor", V("Z"), V("Y"))])

    print("Query: ancestor(alice, Who)")
    for sol in kb.query(A("ancestor", "alice", V("Who")), max_solutions=10):
        print(sol)

    print("\nQuery: parent(Who, carol)")
    for sol in kb.query(A("parent", V("Who"), "carol")):
        print(sol)
