import csv
import json
from pathlib import Path
from typing import List
from models import AnalysisResult

FIELDS = ["source", "subject", "sender", "date", "summary", "priority", "category",
          "action_items", "deadlines", "engine", "confidence", "notes"]

def save_reports(results: List[AnalysisResult], output_dir="output"):
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    json_path = out / "email_summary.json"
    csv_path = out / "email_summary.csv"
    data = [r.to_dict() for r in results]
    json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    with csv_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        for row in data:
            row = row.copy()
            row["action_items"] = " | ".join(row["action_items"])
            row["deadlines"] = " | ".join(row["deadlines"])
            writer.writerow(row)
    return csv_path, json_path
