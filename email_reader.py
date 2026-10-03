from pathlib import Path
from typing import List
from models import EmailMessage

HEADER_KEYS = {"from": "sender", "subject": "subject", "date": "date"}

def parse_email_text(text: str, source: str = "pasted_email") -> EmailMessage:
    values = {"sender": "Unknown", "subject": Path(source).stem, "date": "Unknown"}
    body_lines = []
    in_headers = True
    for line in text.replace("\r\n", "\n").split("\n"):
        if in_headers and not line.strip():
            in_headers = False
            continue
        if in_headers and ":" in line:
            key, value = line.split(":", 1)
            normalized = key.strip().lower()
            if normalized in HEADER_KEYS:
                values[HEADER_KEYS[normalized]] = value.strip() or values[HEADER_KEYS[normalized]]
                continue
        body_lines.append(line)
    body = "\n".join(body_lines).strip()
    if not body:
        body = text.strip()
    return EmailMessage(source, values["subject"], values["sender"], values["date"], body)

def read_email_file(path: Path) -> EmailMessage:
    return parse_email_text(path.read_text(encoding="utf-8", errors="replace"), path.name)

def read_email_folder(folder: str) -> List[EmailMessage]:
    folder_path = Path(folder)
    if not folder_path.exists():
        raise FileNotFoundError(f"Input folder not found: {folder}")
    return [read_email_file(p) for p in sorted(folder_path.glob("*.txt"))]
