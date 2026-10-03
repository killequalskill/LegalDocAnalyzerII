import re
from typing import Optional


def detect_section_heading(line: str) -> bool:
    """
    Heuristic to detect if a line looks like a section heading.

    Indicators:
    - All or mostly uppercase
    - Short (< 80 chars)
    - Contains common legal section markers
    """
    stripped = line.strip()

    if not stripped or len(stripped) > 80:
        return False

    # Check for common legal markers
    if any(marker in stripped.upper() for marker in [
        "ARTICLE", "SECTION", "CLAUSE", "WHEREAS", "RECITALS",
        "DEFINITIONS", "TERM", "TERMINATION", "PAYMENT", "CONFIDENTIALITY",
        "LIABILITY", "INDEMNIFICATION", "INTELLECTUAL PROPERTY",
        "DISPUTE RESOLUTION", "NON-COMPETE", "DATA PROTECTION",
        "GOVERNING LAW", "RENEWAL"
    ]):
        return True

    # Check if line is mostly uppercase
    if len(stripped) > 5:
        upper_ratio = sum(1 for c in stripped if c.isupper()) / len(stripped)
        if upper_ratio > 0.6:
            return True

    return False


def detect_clause_id(line: str) -> Optional[str]:
    """
    Extract clause ID if present (e.g., "7.2", "Article 5").
    Returns the matched ID or None.
    """
    # Match patterns like "7.2", "7.2.1", "Article 5", "Section 3"
    patterns = [
        r'^(\d+\.\d+(?:\.\d+)?)',  # 7.2, 7.2.1
        r'^(Article\s+\d+)',        # Article 5
        r'^(Section\s+\d+)',        # Section 3
    ]

    for pattern in patterns:
        match = re.match(pattern, line.strip(), re.IGNORECASE)
        if match:
            return match.group(1)

    return None


def estimate_tokens(text: str) -> int:
    """
    Rough token count using word-based heuristic.
    Assumes ~1.3 tokens per word on average.
    """
    words = len(text.split())
    return int(words * 1.3)
