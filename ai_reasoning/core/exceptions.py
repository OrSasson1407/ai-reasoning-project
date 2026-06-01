"""
AI Reasoning Project — Architectural Exceptions
Centralizes all Contract Violations (CV) and Protocol Invariants (CI, DI).
"""

class AIReasoningArchitecturalError(Exception):
    """Base class for all non-recoverable architectural violations."""
    pass

class QuarantineBypassError(AIReasoningArchitecturalError):
    """CV-006: Raised when the inference engine attempts to read a quarantined node."""
    pass

class ConfidenceInflationError(AIReasoningArchitecturalError):
    """CV-004 / CV-005: Raised when inductive/abductive confidence caps are exceeded."""
    pass

class SilentMutationError(AIReasoningArchitecturalError):
    """CV-007: Raised when state is mutated without an audit_log_ref."""
    pass

class SafetyViolationError(AIReasoningArchitecturalError):
    """CV-008: Raised when a conclusion fails the Values Constraint Layer (VCL)."""
    pass

class HypothesisIsolationError(AIReasoningArchitecturalError):
    """CI-09: Raised when a Hypothesis (conf <= 0.50) is used as the sole premise for Deduction."""
    pass
