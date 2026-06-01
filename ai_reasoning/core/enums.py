"""
AI Reasoning Project — Enumerations
Sourced from: DAD v1.0 §2.2, §3.2 · RRS v1.0 §6.2
"""

from enum import Enum


class NodeType(str, Enum):
    PHYSICAL_OBJECT     = "PHYSICAL_OBJECT"
    BIOLOGICAL_ENTITY   = "BIOLOGICAL_ENTITY"
    PERSON              = "PERSON"
    ORGANISATION        = "ORGANISATION"
    EVENT               = "EVENT"
    PROCESS             = "PROCESS"
    LAW_OR_RULE         = "LAW_OR_RULE"
    HYPOTHESIS          = "HYPOTHESIS"
    ABSTRACT_CONCEPT    = "ABSTRACT_CONCEPT"
    MATHEMATICAL_OBJECT = "MATHEMATICAL_OBJECT"
    MEASUREMENT         = "MEASUREMENT"
    CLAIM               = "CLAIM"


class RelationType(str, Enum):
    CAUSES          = "CAUSES"
    ENABLES         = "ENABLES"
    PREVENTS        = "PREVENTS"
    PRECEDES        = "PRECEDES"
    SUPPORTS        = "SUPPORTS"
    CONTRADICTS     = "CONTRADICTS"
    IS_A            = "IS_A"
    PART_OF         = "PART_OF"
    HAS_PROPERTY    = "HAS_PROPERTY"
    CORRELATED_WITH = "CORRELATED_WITH"
    ANALOGOUS_TO    = "ANALOGOUS_TO"
    DERIVED_FROM    = "DERIVED_FROM"
    REPLACES        = "REPLACES"
    HYPOTHESISED_BY = "HYPOTHESISED_BY"


class EpistemicModel(str, Enum):
    BAYESIAN        = "BAYESIAN"
    DEMPSTER_SHAFER = "DEMPSTER_SHAFER"
    FUZZY           = "FUZZY"


class ConfidenceLevel(str, Enum):
    VERIFIED     = "VERIFIED"
    HIGH         = "HIGH"
    MODERATE     = "MODERATE"
    LOW          = "LOW"
    VERY_LOW     = "VERY_LOW"
    CONTRADICTED = "CONTRADICTED"

    @classmethod
    def from_score(cls, score: float) -> "ConfidenceLevel":
        if score >= 0.90: return cls.VERIFIED
        if score >= 0.70: return cls.HIGH
        if score >= 0.50: return cls.MODERATE
        if score >= 0.30: return cls.LOW
        if score >= 0.05: return cls.VERY_LOW
        return cls.CONTRADICTED


class ReasoningMode(str, Enum):
    DEDUCTIVE = "DEDUCTIVE"
    INDUCTIVE = "INDUCTIVE"
    ABDUCTIVE = "ABDUCTIVE"


class SourceType(str, Enum):
    PEER_REVIEWED   = "PEER_REVIEWED"
    OFFICIAL_RECORD = "OFFICIAL_RECORD"
    NEWS_OUTLET     = "NEWS_OUTLET"
    EXPERT_CLAIM    = "EXPERT_CLAIM"
    USER_ASSERTION  = "USER_ASSERTION"
    INFERENCE       = "INFERENCE"
    UNKNOWN         = "UNKNOWN"


class ContradictionSeverity(str, Enum):
    HALT = "HALT"
    FLAG = "FLAG"
    WARN = "WARN"


class ResolutionStatus(str, Enum):
    UNRESOLVED  = "UNRESOLVED"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED    = "RESOLVED"
    ESCALATED   = "ESCALATED"
