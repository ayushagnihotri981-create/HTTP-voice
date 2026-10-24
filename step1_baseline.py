"""
VoiceOps 2026 - Step 1: Answer a question with an LLM (prompt only, no documents).

Runs the ZentroMart support assistant on practice/questions.csv and saves the
answers so you can count how many it gets right. Step 2 (RAG) should beat this.

Usage:
    # Option A: Run with your real OpenAI API key
    python step1_baseline.py --questions practice/questions.csv

    # Option B: Run in simulation / mock mode (tests pipeline end-to-end without API key)
    python step1_baseline.py --questions practice/questions.csv --mock
"""

import argparse
import csv
import os
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
    # Load .env from current directory or script parent directory
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
    else:
        load_dotenv()
except ImportError:
    pass

import pandas as pd
from openai import OpenAI

DEFAULT_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
OUTPUT_DIR = Path("outputs/step1")

SYSTEM_PROMPT = """You are the customer support assistant for ZentroMart, an online store
selling groceries and electronics in India.

Rules:
- In your first reply in a conversation, tell the customer you are an AI assistant.
- You have not been given ZentroMart's policy documents. If you are unsure of a policy,
  date, or amount, say you are not certain and offer to connect the customer to a human.
  Never invent a policy, date, or amount.
- Keep replies short and clear, since they may be spoken aloud.
- Ask for the order ID when a question is about a specific order.
"""


def load_questions(path: Path) -> pd.DataFrame:
    # Keep every field as a string so IDs like "001" keep their leading zeros.
    df = pd.read_csv(path, dtype=str).fillna("")
    if "question" not in df.columns:
        sys.exit(f"Expected a 'question' column in {path}. Found: {list(df.columns)}")
    if "asr_text" in df.columns:
        # asr_text simulates transcription of the spoken question; prefer it when present.
        df["input_text"] = df["asr_text"].where(df["asr_text"].str.strip() != "", df["question"])
    else:
        df["input_text"] = df["question"]
    return df


def ask(client: OpenAI, model: str, question: str) -> str:
    response = client.chat.completions.create(
        model=model,
        max_tokens=400,
        temperature=0.0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question},
        ],
    )
    return response.choices[0].message.content.strip()


def mock_ask(question: str) -> str:
    """Simulates prompt-only LLM baseline behavior adhering to the system prompt."""
    q_lower = question.lower()
    prefix = "Hello! I am the ZentroMart AI assistant. "

    if "milk" in q_lower or "perishable" in q_lower:
        return (
            prefix
            + "I don't have access to our specific grocery return policy details, so I am not certain if the milk packet can be returned. "
            + "Would you like me to connect you with a human support agent?"
        )
    elif "where is my order" in q_lower or "tracking" in q_lower:
        return (
            prefix
            + "I would be happy to check that for you. Could you please provide your Order ID?"
        )
    elif "sound" in q_lower or "soundbar" in q_lower or "electronics" in q_lower:
        return (
            prefix
            + "I do not have the exact return policy document for electronics on hand, so I cannot confirm the return window. "
            + "I can connect you to a customer care representative who can assist you immediately."
        )
    elif "broken eggs" in q_lower or "zm" in q_lower:
        return (
            prefix
            + "I am sorry to hear about the damaged items in your order. "
            + "Since I do not have direct access to process refunds or verify store policies, let me connect you to a human agent right away."
        )
    elif "phone number" in q_lower or "helpline" in q_lower or "customer care" in q_lower:
        return (
            prefix
            + "I do not have the verified customer care helpline number in my prompt guidelines. "
            + "Please check the ZentroMart mobile app or website, or let me connect you to human support."
        )
    elif "pune" in q_lower or "hyderabad" in q_lower or "deliver" in q_lower:
        return (
            prefix
            + "I am not certain of our current delivery coverage cities. "
            + "I can connect you to a representative to verify delivery availability for your PIN code."
        )
    elif "cancel" in q_lower:
        return (
            prefix
            + "Could you please provide your Order ID so I can check? Please note I am not certain of the exact cancellation cutoff rules."
        )
    elif "upi refund" in q_lower or "refund take" in q_lower:
        return (
            prefix
            + "I am not certain about the exact refund timeframe for UPI payments. "
            + "Would you like me to connect you to a human support agent for accurate details?"
        )
    else:
        return (
            prefix
            + "I am not certain about this policy. Would you like me to connect you to a human agent?"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="VoiceOps 2026 - Step 1 prompt-only baseline (OpenAI)")
    parser.add_argument("--questions", required=True, type=Path, help="Path to practice/questions.csv")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"OpenAI model name (default: {DEFAULT_MODEL})")
    parser.add_argument("--mock", action="store_true", help="Run simulated responses (no API key required)")
    args = parser.parse_args()

    client = None
    if not args.mock:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key or api_key == "your_openai_api_key_here":
            print("Note: No OPENAI_API_KEY detected. Defaulting to --mock simulation mode.")
            print("To use live OpenAI API calls, set OPENAI_API_KEY in your .env file.\n")
            args.mock = True
        else:
            client = OpenAI(api_key=api_key)

    df = load_questions(args.questions)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / "step1_answers.csv"

    rows = []
    mode_str = f"Live OpenAI API ({args.model})" if not args.mock else "Mock Simulation Mode"
    print(f"=== VoiceOps 2026: Step 1 Baseline Evaluation ===")
    print(f"Mode: {mode_str}")
    print(f"Total Questions: {len(df)}\n")

    for i, row in df.iterrows():
        question_id = row.get("question_id", str(i + 1))
        input_text = row["input_text"]
        if args.mock:
            answer = mock_ask(input_text)
        else:
            answer = ask(client, args.model, input_text)

        rows.append({
            "question_id": question_id,
            "input_text": input_text,
            "answer": answer,
        })
        print(f"[{i + 1}/{len(df)}] Q({question_id}): Answered")

    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["question_id", "input_text", "answer"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nSaved {len(rows)} answers to {out_path}")
    print("Run `python grade_step1.py` to evaluate your baseline score!")


if __name__ == "__main__":
    main()
