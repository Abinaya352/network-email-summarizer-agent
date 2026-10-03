import logging
from pathlib import Path
from typing import List
from models import EmailMessage, AnalysisResult
from rule_engine import analyze_with_rules

class EmailSummarizerAgent:
    def __init__(self, engine="rules", log_path="output/agent.log"):
        self.engine = engine
        Path(log_path).parent.mkdir(parents=True, exist_ok=True)
        logging.basicConfig(filename=log_path, level=logging.INFO,
                            format="%(asctime)s %(levelname)s %(message)s")

    def run(self, email: EmailMessage) -> AnalysisResult:
        logging.info("OBSERVE source=%s subject=%s", email.source, email.subject)
        selected = self.engine.lower()
        logging.info("PLAN engine=%s", selected)
        if selected == "llm":
            try:
                from llm_engine import analyze_with_llm
                result = analyze_with_llm(email)
                logging.info("ACT llm_success source=%s", email.source)
            except Exception as exc:
                logging.exception("ACT llm_failed; falling back to rules")
                result = analyze_with_rules(email)
                result.notes = f"LLM unavailable; used safe rule fallback: {type(exc).__name__}"
        else:
            result = analyze_with_rules(email)
            logging.info("ACT rules_success source=%s", email.source)
        result.validate()
        logging.info("EVALUATE valid priority=%s category=%s", result.priority, result.category)
        return result

    def run_batch(self, emails: List[EmailMessage]) -> List[AnalysisResult]:
        return [self.run(email) for email in emails]
