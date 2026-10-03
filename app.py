import json
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from agent import EmailSummarizerAgent
from email_reader import parse_email_text
from report_generator import save_reports

load_dotenv()
st.set_page_config(page_title="Email Summarizer Agent", page_icon="📧", layout="wide")
st.title("📧 Network Operations Email Summarizer Agent")
st.caption("Read-only demo: summarize, classify, prioritize, and extract actions from operational emails.")

engine = st.sidebar.selectbox("Analysis engine", ["rules", "llm"],
                              format_func=lambda x: "Rule-based (offline)" if x == "rules" else "LLM (configured provider)")
mode = st.radio("Choose input", ["Paste email", "Upload .txt files"], horizontal=True)
messages = []
if mode == "Paste email":
    sample = """From: noc@example.com
Subject: Packet loss detected on core link
Date: 2026-10-03 20:15 IST

Critical alert: packet loss is affecting the core link. Please validate interface errors and update the incident by EOD."""
    text = st.text_area("Email content", value=sample, height=220)
    if text.strip():
        messages = [parse_email_text(text)]
else:
    uploads = st.file_uploader("Upload email text files", type=["txt"], accept_multiple_files=True)
    for item in uploads:
        messages.append(parse_email_text(item.getvalue().decode("utf-8", errors="replace"), item.name))

if st.button("Analyze", type="primary", disabled=not messages):
    with st.spinner("Analyzing..."):
        agent = EmailSummarizerAgent(engine)
        results = agent.run_batch(messages)
        save_reports(results)
    st.success(f"Analyzed {len(results)} email(s).")
    rows = []
    for result in results:
        rows.append({
            "Subject": result.subject, "Priority": result.priority, "Category": result.category,
            "Summary": result.summary, "Actions": " | ".join(result.action_items) or "None found",
            "Deadlines": " | ".join(result.deadlines) or "None found", "Engine": result.engine,
            "Confidence": result.confidence, "Notes": result.notes,
        })
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.download_button("Download CSV", df.to_csv(index=False).encode("utf-8"),
                       "email_summary.csv", "text/csv")
    st.download_button("Download JSON", json.dumps([r.to_dict() for r in results], indent=2),
                       "email_summary.json", "application/json")
