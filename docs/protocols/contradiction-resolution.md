# Contradiction Resolution Protocol
When a contradiction is detected:
1. **Detection:** The CCP Detector identifies a CONTRADICTS relation.
2. **Quarantine:** Involved nodes and their DERIVED_FROM descendants are immediately quarantined (CI-05).
3. **Escalation:** If Level 1 (HALT) is triggered, the system pauses operation on that branch.
4. **Resolution:** An explicit human or meta-cognitive resolution event must be recorded (CI-03, CI-07).
5. **Release:** Once resolved, quarantine is lifted, and the audit log is updated (DI-09).
