import re
from collections import Counter
from models import EmailMessage, AnalysisResult

CATEGORY_WORDS = {
    "Incident": ["incident", "outage", "down", "alarm", "packet loss", "degraded", "flap", "unreachable", "critical alert"],
    "Maintenance": ["maintenance", "maintenance window", "planned work", "scheduled work", "upgrade"],
    "Change Request": ["change request", "change ticket", "implementation", "rollback", "crq", "change window"],
    "Vendor Update": ["vendor", "carrier", "isp", "provider", "field engineer", "rma"],
    "Approval Request": ["approve", "approval", "sign-off", "authorization", "review and confirm"],
}

PRIORITY_WORDS = {
    "Critical": ["sev1", "p1", "critical", "major outage", "service down", "immediate action"],
    "High": ["sev2", "p2", "high priority", "urgent", "packet loss", "degraded", "approval required"],
    "Low": ["low priority", "for your information", "fyi", "no action required", "informational"],
}

ACTION_PATTERNS = [
    r"(?i)(?:please|kindly)\s+([^.!?\n]+)",
    r"(?i)(?:action required|action item)\s*[:\-]\s*([^.!?\n]+)",
    r"(?i)(?:need to|must|should)\s+([^.!?\n]+)",
]

DEADLINE_PATTERNS = [
    r"(?i)\b(?:by|before|deadline:?|due:?)\s+([^.!?\n]+)",
    r"(?i)\b(?:today|tomorrow|eod|end of day)\b",
    r"\b\d{4}-\d{2}-\d{2}(?:\s+\d{1,2}:\d{2})?\b",
]

def _sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", text) if len(s.strip()) > 10]

def _category(text):
    scores = {cat: sum(text.count(word) for word in words) for cat, words in CATEGORY_WORDS.items()}
    best, score = max(scores.items(), key=lambda x: x[1])
    return (best, min(0.95, 0.55 + score * 0.08)) if score else ("General", 0.45)

def _priority(text):
    for level in ("Critical", "High", "Low"):
        if any(word in text for word in PRIORITY_WORDS[level]):
            return level
    return "Medium"

def _summary(body, max_sentences=2):
    sentences = _sentences(body)
    if not sentences:
        return body[:280] if body else "No content available."
    tokens = re.findall(r"[a-zA-Z]{3,}", body.lower())
    common = Counter(t for t in tokens if t not in {"the", "and", "for", "this", "that", "with", "from", "have", "will", "your", "you", "are"})
    ranked = sorted(enumerate(sentences), key=lambda p: sum(common[w] for w in re.findall(r"[a-zA-Z]{3,}", p[1].lower())), reverse=True)
    chosen = sorted(ranked[:max_sentences], key=lambda p: p[0])
    return " ".join(s for _, s in chosen)[:600]

def _extract(patterns, text, limit=5):
    values = []
    for pattern in patterns:
        for match in re.findall(pattern, text):
            value = match if isinstance(match, str) else " ".join(match)
            value = value.strip(" :-\t")
            if value and value.lower() not in [x.lower() for x in values]:
                values.append(value)
    return values[:limit]

def analyze_with_rules(email: EmailMessage) -> AnalysisResult:
    text = f"{email.subject}\n{email.body}".lower()
    category, confidence = _category(text)
    return AnalysisResult(
        source=email.source, subject=email.subject, sender=email.sender, date=email.date,
        summary=_summary(email.body), priority=_priority(text), category=category,
        action_items=_extract(ACTION_PATTERNS, email.body),
        deadlines=_extract(DEADLINE_PATTERNS, email.body),
        engine="rules", confidence=confidence,
    ).validate()
