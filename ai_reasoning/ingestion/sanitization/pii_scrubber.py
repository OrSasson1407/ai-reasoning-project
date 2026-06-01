"""
AI Reasoning Project — Data Sanitization
Ensures personally identifiable information (PII) is masked before entering the World Model.
"""
import re

class PIIScrubber:
    """Scrub raw text to prevent sensitive data leakage into the Knowledge Graph."""
    
    EMAIL_REGEX = re.compile(r"[\w\.-]+@[\w\.-]+\.\w+")
    PHONE_REGEX = re.compile(r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}")

    @classmethod
    def scrub(cls, text: str) -> str:
        if not text:
            return text
            
        text = cls.EMAIL_REGEX.sub("[EMAIL_REDACTED]", text)
        text = cls.PHONE_REGEX.sub("[PHONE_REDACTED]", text)
        return text
