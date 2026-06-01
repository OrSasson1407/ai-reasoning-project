"""
AI Reasoning Project — System Audit Logger
Sourced from: DAD DI-09 · CCP CI-07
"""

import json
import uuid
from datetime import datetime, timezone
import logging

class StrictAuditLogger:
    """
    Enforces Rule DI-09 & CI-07: Audit Log Mandatory.
    Silent writes or contradiction resolutions are architecturally forbidden.
    """
    def __init__(self, log_path: str = "system_audit.log"):
        self.logger = logging.getLogger("AI_Reasoning_Audit")
        self.logger.setLevel(logging.INFO)
        handler = logging.FileHandler(log_path)
        handler.setFormatter(logging.Formatter('%(message)s'))
        self.logger.addHandler(handler)

    def log_mutation(self, action: str, entity_id: uuid.UUID, actor: str, context: dict) -> str:
        """
        Logs a strict state mutation. Returns the audit_log_ref needed to satisfy CV-007.
        """
        audit_id = str(uuid.uuid4())
        entry = {
            "audit_id": audit_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "entity_id": str(entity_id),
            "actor": actor,
            "context": context
        }
        self.logger.info(json.dumps(entry))
        return audit_id
