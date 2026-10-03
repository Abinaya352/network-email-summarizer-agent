# Network Operations Email Summarizer Agent

A beginner-friendly Agentic AI project that reads `.txt` email files, summarizes them, assigns a category and priority, extracts action items and deadlines, and exports daily reports.

## Why it is agentic

The controller follows a bounded loop:

1. **Observe**: read email text and metadata.
2. **Plan**: choose rule-based processing or an available LLM tool.
3. **Act**: summarize, classify, and extract actions.
4. **Evaluate**: validate the structured output and repair missing fields.
5. **Stop**: save the result after one safe processing cycle.

This is intentionally read-only. It does not send, delete, or modify emails.

## Features

- Works offline using a deterministic rule-based engine
- Optional OpenAI or Azure OpenAI integration
- Network-operations categories: Incident, Maintenance, Change Request, Vendor Update, Approval Request, General
- Priority detection: Critical, High, Medium, Low
- Action-item and deadline extraction
- Streamlit demo UI
- CLI batch processing
- CSV and JSON reports
- Audit log (`output/agent.log`)
- Unit tests

## Project structure

```text
network_email_summarizer_agent/
├── app.py
├── main.py
├── agent.py
├── models.py
├── email_reader.py
├── rule_engine.py
├── llm_engine.py
├── report_generator.py
├── requirements.txt
├── .env.example
├── README.md
├── emails/
│   ├── incident_alert.txt
│   ├── maintenance_notice.txt
│   └── approval_request.txt
├── output/
└── tests/
    └── test_agent.py
```

## Quick start

### 1. Create a virtual environment

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the command-line version

```bash
python main.py --input emails --output output
```

Generated files:

- `output/email_summary.csv`
- `output/email_summary.json`
- `output/agent.log`

### 4. Run the UI

```bash
streamlit run app.py
```

Choose **Rule-based** first. Paste an email or upload `.txt` files, then select **Analyze**.

## Optional LLM setup

Copy `.env.example` to `.env` and configure one provider. Do not commit `.env`.

### OpenAI

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=your_key
OPENAI_MODEL=gpt-4.1-mini
```

### Azure OpenAI

```env
LLM_PROVIDER=azure
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_ENDPOINT=https://YOUR-RESOURCE.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=your_deployment_name
AZURE_OPENAI_API_VERSION=2024-10-21
```

Use only tools and credentials approved by your organization. Do not paste production-sensitive email content into an unapproved external service.

## Input file format

```text
From: vendor@example.com
Subject: Planned maintenance for edge router
Date: 2026-10-10 22:00 IST

Hello Team,
The edge router will undergo maintenance...
```

Headers are optional. The filename becomes the subject when `Subject:` is missing.

## CLI options

```bash
python main.py --input emails --output output --engine rules
python main.py --input emails --output output --engine llm
```

If `--engine llm` fails because configuration is unavailable, the agent safely falls back to rules and records the reason in the result and audit log.

## Run tests

```bash
python -m unittest discover -s tests -v
```

