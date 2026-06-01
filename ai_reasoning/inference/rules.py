from dataclasses import dataclass
from ai_reasoning.core.enums import ReasoningMode

@dataclass
class ReasoningRule:
    mode: ReasoningMode
    description: str = 'Default'
    rule_id: str = 'default_rule'

class ReasoningRuleProcessor:
    def __init__(self, mode: ReasoningMode = None): self.mode = mode
    def calculate_confidence(self, premises_conf: list) -> float:
        if not premises_conf: return 0.0
        if self.mode == ReasoningMode.DEDUCTIVE: return min(premises_conf) * 0.95
        elif self.mode == ReasoningMode.INDUCTIVE: return min(0.85, sum(premises_conf) / len(premises_conf))
        elif self.mode == ReasoningMode.ABDUCTIVE: return min(0.50, sum(premises_conf) / len(premises_conf))
        return 0.5
    def process(self, rule: ReasoningRule, context: dict): return True
