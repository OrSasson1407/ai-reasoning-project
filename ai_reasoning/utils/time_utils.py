from datetime import datetime, timezone

def now_iso() -> str:
    """Returns strict ISO-8601 timestamp for AIC API Contracts."""
    return datetime.now(timezone.utc).isoformat()
