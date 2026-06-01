"""
Confidence Propagation Rules — RRS v1.0 §6
UP-01 through UP-10
"""

from .enums import ConfidenceLevel

INDUCTIVE_CAP = 0.85   # UP-06
ABDUCTIVE_CAP = 0.50   # UP-07
FLOOR         = 0.05   # UP-10
CHAIN_WARN    = 5      # MCT-06


def conjunction(a: float, b: float) -> float:
    """UP-01: conf(A AND B) = conf(A) * conf(B)"""
    return round(a * b, 6)

def disjunction(a: float, b: float) -> float:
    """UP-02: conf(A OR B) = 1 - (1-a)(1-b)"""
    return round(1.0 - (1.0 - a) * (1.0 - b), 6)

def negation(a: float) -> float:
    """UP-03: conf(NOT A) = 1 - conf(A)"""
    return round(1.0 - a, 6)

def chain_penalty(confidences: list[float]) -> tuple[float, bool]:
    """UP-04: multiply all steps; flag if chain >= CHAIN_WARN."""
    result = 1.0
    for c in confidences:
        result *= c
    result = max(FLOOR, round(result, 6))
    warned = len(confidences) >= CHAIN_WARN
    return result, warned

def causal_propagation(cause_conf: float, causal_strength: float,
                        condition_score: float = 1.0) -> float:
    """UP-05: conf(effect) = conf(cause) * causal_strength * condition_score"""
    return max(FLOOR, round(cause_conf * causal_strength * condition_score, 6))

def apply_inductive_cap(conf: float) -> float:
    """UP-06: inductive conclusions cap at 0.85"""
    return min(conf, INDUCTIVE_CAP)

def apply_abductive_cap(conf: float) -> float:
    """UP-07: abductive conclusions (hypotheses) cap at 0.50"""
    return min(conf, ABDUCTIVE_CAP)

def bayesian_update(prior: float, likelihood: float, evidence_prob: float) -> float:
    """UP-08: P(H|E) = P(E|H)*P(H) / P(E)"""
    if evidence_prob <= 0:
        raise ValueError("evidence_prob must be > 0")
    updated = (likelihood * prior) / evidence_prob
    return max(FLOOR, min(1.0, round(updated, 6)))

def ignorance_interval(belief: float, plausibility: float) -> tuple[float, float]:
    """UP-09: Dempster-Shafer interval — Belief <= reported <= Plausibility"""
    if belief > plausibility:
        raise ValueError("belief must be <= plausibility")
    return round(belief, 6), round(plausibility, 6)

def apply_floor(conf: float, contradicted: bool = False) -> float:
    """UP-10: floor is 0.05 normally; 0.0 only for actively contradicted."""
    if contradicted:
        return max(0.0, conf)
    return max(FLOOR, conf)
