import os, uuid, tempfile
from ai_reasoning.storage.audit import StrictAuditLogger

def test_audit_log_creation():
    fd, test_log = tempfile.mkstemp(suffix='.log')
    os.close(fd)
    try:
        logger = StrictAuditLogger(test_log)
        audit_id = logger.log_mutation(
            action='TEST_ACTION', entity_id=uuid.uuid4(), actor='test', context={'reason': 'DI-09 validation'}
        )
        with open(test_log, 'r') as f:
            content = f.read()
            assert str(audit_id) in content
            assert 'TEST_ACTION' in content
    finally:
        if os.path.exists(test_log):
            try: os.remove(test_log)
            except: pass
