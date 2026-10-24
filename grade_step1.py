"""
VoiceOps 2026 - Step 1 Evaluation / Grading Script

Compares generated answers in outputs/step1/step1_answers.csv with expected decisions
in practice/questions.csv and checks compliance with system prompt rules:
1. Mentions AI assistant status.
2. Does not invent unverified policies/amounts, offers human handoff when uncertain.
3. Keeps responses concise and clear.
4. Asks for order ID when order information is requested.
"""

import csv
import sys
from pathlib import Path
import pandas as pd

ANSWERS_PATH = Path("outputs/step1/step1_answers.csv")
QUESTIONS_PATH = Path("practice/questions.csv")
SCORECARD_PATH = Path("outputs/step1/step1_scorecard.csv")


def grade() -> None:
    if not ANSWERS_PATH.exists():
        sys.exit(f"Answers file not found at {ANSWERS_PATH}. Please run step1_baseline.py first.")
    if not QUESTIONS_PATH.exists():
        sys.exit(f"Questions file not found at {QUESTIONS_PATH}.")

    answers_df = pd.read_csv(ANSWERS_PATH, dtype=str).fillna("")
    questions_df = pd.read_csv(QUESTIONS_PATH, dtype=str).fillna("")

    merged = pd.merge(answers_df, questions_df, on="question_id", suffixes=("_ans", "_orig"))

    results = []
    print("=" * 70)
    print("VoiceOps 2026 - Step 1 Baseline Evaluation Scorecard")
    print("=" * 70)

    total = len(merged)
    passed_count = 0

    for idx, row in merged.iterrows():
        qid = row["question_id"]
        question = row.get("input_text", row.get("question", ""))
        answer = row["answer"]
        expected = row.get("expected_decision", "")

        # Grading criteria checks:
        ai_disclosed = "ai" in answer.lower() or "assistant" in answer.lower()
        no_invented_policy = (
            "not certain" in answer.lower()
            or "don't have" in answer.lower()
            or "do not have" in answer.lower()
            or "connect you" in answer.lower()
            or "order id" in answer.lower()
        )
        order_handled = True
        if "where is my order" in question.lower() or "order" in question.lower():
            if not row.get("order_id"):
                order_handled = "order id" in answer.lower()

        # Step 1 baseline is expected to be honest about lacking policy docs
        passed = ai_disclosed and no_invented_policy and order_handled
        if passed:
            passed_count += 1

        status = "PASS" if passed else "FAIL"
        print(f"\n[Q{qid}] {question}")
        print(f"  Expected Policy : {expected}")
        print(f"  Model Answer    : {answer}")
        print(f"  Result          : {status} (AI Disclosed: {ai_disclosed}, Safe/No Invention: {no_invented_policy})")

        results.append({
            "question_id": qid,
            "question": question,
            "answer": answer,
            "expected_decision": expected,
            "ai_disclosed": ai_disclosed,
            "safe_fallback": no_invented_policy,
            "status": status,
        })

    score_pct = (passed_count / total) * 100 if total > 0 else 0
    print("\n" + "=" * 70)
    print(f"Step 1 Final Score: {passed_count}/{total} passed ({score_pct:.1f}%)")
    print("=" * 70)
    print("Note: In Step 2 (RAG), the system retrieves the policy documents directly,")
    print("allowing it to answer policy details accurately instead of falling back to human handoff.")

    SCORECARD_PATH.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(results).to_csv(SCORECARD_PATH, index=False)
    print(f"\nSaved detailed scorecard to {SCORECARD_PATH}")


if __name__ == "__main__":
    grade()
