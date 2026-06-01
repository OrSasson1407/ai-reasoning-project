import pytest
import os
import uuid
from ai_reasoning.storage.audit import StrictAuditLogger

def test_audit_log_creation():
    """Rule DI-09 / CI-07: Ensure audit logs are actually written."""
    test_log = "test_audit.log"
    logger = StrictAuditLogger(test_log)
    
    audit_id = logger.log_mutation(
        action="TEST_ACTION",
        entity_id=uuid.uuid4(),
        actor="system_test",
        context={"reason": "DI-09 validation"}
    )
    
    assert os.path.exists(test_log)
    
    with open(test_log, "r") as f:
        content = f.read()
        assert audit_id in content
        assert "TEST_ACTION" in content

    # Cleanup
    if os.path.exists(test_log):
        os.remove(test_log)
