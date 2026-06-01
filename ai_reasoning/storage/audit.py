import json, uuid, logging
from datetime import datetime, timezone

class StrictAuditLogger:
    def __init__(self, log_file: str = "security_audit.log"):
        self.logger = logging.getLogger("AI_Audit")
        if not self.logger.handlers:
            self.logger.addHandler(logging.FileHandler(log_file))
            self.logger.setLevel(logging.INFO)
    def log_mutation(self, action: str, entity_id: uuid.UUID, actor: str, context: dict) -> str:
        aid = str(uuid.uuid4())
        self.logger.info(json.dumps({"audit_id": aid, "action": action, "entity_id": str(entity_id)}))
        return aid
