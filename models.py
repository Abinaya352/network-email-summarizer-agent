from dataclasses import dataclass, asdict, field
from typing import List

VALID_PRIORITIES = {"Critical", "High", "Medium", "Low"}
VALID_CATEGORIES = {
    "Incident", "Maintenance", "Change Request", "Vendor Update",
    "Approval Request", "General"
}

@dataclass
class EmailMessage:
    source: str
    subject: str
    sender: str
    date: str
    body: str

@dataclass
class AnalysisResult:
    source: str
    subject: str
    sender: str
    date: str
    summary: str
    priority: str
    category: str
    action_items: List[str] = field(default_factory=list)
    deadlines: List[str] = field(default_factory=list)
    engine: str = "rules"
    confidence: float = 0.0
    notes: str = ""

    def validate(self):
        if self.priority not in VALID_PRIORITIES:
            self.priority = "Medium"
        if self.category not in VALID_CATEGORIES:
            self.category = "General"
        self.summary = (self.summary or "No summary available.").strip()
        self.action_items = [str(x).strip() for x in self.action_items if str(x).strip()]
        self.deadlines = [str(x).strip() for x in self.deadlines if str(x).strip()]
        self.confidence = max(0.0, min(float(self.confidence), 1.0))
        return self

    def to_dict(self):
        return asdict(self)
