import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from agent import EmailSummarizerAgent
from email_reader import parse_email_text

class TestAgent(unittest.TestCase):
    def test_incident_priority_and_actions(self):
        mail = parse_email_text("""From: noc@example.com
Subject: Critical service outage

Critical service down. Please check the router immediately and update the incident by EOD.""")
        result = EmailSummarizerAgent("rules", "output/test.log").run(mail)
        self.assertEqual(result.category, "Incident")
        self.assertEqual(result.priority, "Critical")
        self.assertTrue(result.action_items)

    def test_maintenance_classification(self):
        mail = parse_email_text("Subject: Planned maintenance window\n\nA scheduled upgrade will occur tomorrow. No action required.")
        result = EmailSummarizerAgent("rules", "output/test.log").run(mail)
        self.assertEqual(result.category, "Maintenance")
        self.assertEqual(result.priority, "Low")

if __name__ == "__main__":
    unittest.main()
