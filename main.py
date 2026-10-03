import argparse
from dotenv import load_dotenv
from agent import EmailSummarizerAgent
from email_reader import read_email_folder
from report_generator import save_reports

def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description="Network Operations Email Summarizer Agent")
    parser.add_argument("--input", default="emails", help="Folder containing .txt emails")
    parser.add_argument("--output", default="output", help="Report output folder")
    parser.add_argument("--engine", choices=["rules", "llm"], default="rules")
    args = parser.parse_args()
    emails = read_email_folder(args.input)
    if not emails:
        raise SystemExit(f"No .txt email files found in {args.input}")
    agent = EmailSummarizerAgent(args.engine, f"{args.output}/agent.log")
    results = agent.run_batch(emails)
    csv_path, json_path = save_reports(results, args.output)
    print(f"Processed {len(results)} email(s).")
    print(f"CSV report: {csv_path}")
    print(f"JSON report: {json_path}")

if __name__ == "__main__":
    main()
