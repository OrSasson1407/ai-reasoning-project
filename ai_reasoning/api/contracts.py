from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, Any, Dict

class StandardErrorResponse(BaseModel):
    request_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: str = "error"
    error_code: str
    message: str
    detail: Optional[Dict[str, Any]] = None
    trace_id: Optional[str] = None
    retryable: bool = False

class ContractViolations:
    CV_001 = "NO_TRACE: Conclusion delivered without reasoning_trace_id"
    CV_002 = "NO_CONFIDENCE: Conclusion delivered without confidence score"
    CV_003 = "UNPARSED_INPUT: L1 passed free text directly to L2"
    CV_004 = "CONFIDENCE_INFLATION: Inductive conclusion exceeds 0.85 cap"
    CV_005 = "ABDUCTIVE_PROMOTION: Abductive conclusion exceeds 0.50 cap"
    CV_006 = "QUARANTINE_BYPASS: Quarantined node used as inference premise"
    CV_007 = "SILENT_MUTATION: Write to T3 without audit_log_ref"
    CV_008 = "VCL_BYPASS: Conclusion committed without VCL check"
