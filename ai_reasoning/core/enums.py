from enum import Enum

class NodeType(Enum):
    FACT = "FACT"
    HYPOTHESIS = "HYPOTHESIS"
    RULE = "RULE"
    ASSUMPTION = "ASSUMPTION"

class RelationType(Enum):
    DERIVED_FROM = "DERIVED_FROM"
    CONTRADICTS = "CONTRADICTS"
    CAUSES = "CAUSES"
    CORRELATES_WITH = "CORRELATES_WITH"
    SUPPORTS = "SUPPORTS"

class ConfidenceLevel(Enum):
    VERIFIED = (0.90, 1.00)
    HIGH = (0.70, 0.89)
    MODERATE = (0.50, 0.69)
    LOW = (0.30, 0.49)
    VERY_LOW = (0.05, 0.29)
    CONTRADICTED = (0.00, 0.04)

    @classmethod
    def get_level(cls, score: float):
        for level in cls:
            if level.value[0] <= score <= level.value[1]:
                return level
        return cls.CONTRADICTED
