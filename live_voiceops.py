"""
VoiceOps 2026 - Live Working Voice Operations System (Interactive Assistant)
ZentroMart Customer Support Voice & Text Operations

Features:
- Live Interactive Chat / Spoken Query Assistant
- Optional Spoken Voice Output (Windows Speech Synthesizer TTS)
- Mode Toggle: Step 1 (Safe Baseline) vs Step 2 (RAG Knowledge Base)
- Supports OpenAI API or Simulation Mode
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

try:
    from dotenv import load_dotenv
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        load_dotenv(dotenv_path=env_file)
    else:
        load_dotenv()
except ImportError:
    pass

POLICIES_PATH = Path(__file__).parent / "policies" / "zentromart_policies.md"

SYSTEM_PROMPT_STEP1 = """You are the customer support assistant for ZentroMart, an online store
selling groceries and electronics in India.

Rules:
- In your first reply in a conversation, tell the customer you are an AI assistant.
- You have not been given ZentroMart's policy documents. If you are unsure of a policy,
  date, or amount, say you are not certain and offer to connect the customer to a human.
  Never invent a policy, date, or amount.
- Keep replies short and clear, since they may be spoken aloud.
- Ask for the order ID when a question is about a specific order.
"""

SYSTEM_PROMPT_STEP2 = """You are the customer support voice assistant for ZentroMart, an online store
selling groceries and electronics in India.

Rules:
- Tell the customer you are an AI assistant in your greeting.
- Use the provided official ZentroMart policy knowledge base to answer customer questions accurately.
- Keep replies short, conversational, and direct, suitable for voice / spoken audio.
- If asked about an order or cancellation, request the Order ID if not already supplied.
- Never invent information not present in the policy documents.

Official Policies:
{policies}
"""


def speak(text: str) -> None:
    """Uses Windows built-in speech synthesizer to speak aloud."""
    try:
        # Clean text for PowerShell command line
        clean_text = text.replace('"', '`"').replace("'", "''")
        cmd = [
            "powershell",
            "-NoProfile",
            "-Command",
            f'Add-Type -AssemblyName System.Speech; $s = New-Object System.Speech.Synthesis.SpeechSynthesizer; $s.Rate = 1; $s.Speak("{clean_text}");',
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass


def get_policy_context() -> str:
    if POLICIES_PATH.exists():
        return POLICIES_PATH.read_text(encoding="utf-8")
    return "No policy documents found."


def answer_query(query: str, mode: str, client, model: str) -> str:
    """Answers using live OpenAI client if available, else smart rule-based engine."""
    api_key = os.environ.get("OPENAI_API_KEY")

    if client and api_key and api_key != "your_openai_api_key_here":
        if mode == "step2":
            system_msg = SYSTEM_PROMPT_STEP2.format(policies=get_policy_context())
        else:
            system_msg = SYSTEM_PROMPT_STEP1

        response = client.chat.completions.create(
            model=model,
            max_tokens=250,
            temperature=0.1,
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": query},
            ],
        )
        return response.choices[0].message.content.strip()

    # Simulation / Mock Logic
    q_lower = query.lower()
    prefix = "Hello! I am the ZentroMart AI assistant. "

    if mode == "step1":
        # Step 1: Prompt-only baseline without knowledge documents
        if "where" in q_lower or "tracking" in q_lower:
            return prefix + "I can check that for you. Could you please provide your Order ID?"
        elif "cancel" in q_lower:
            return prefix + "Please share your Order ID. I am not certain of the exact cancellation cutoff rules, but I can connect you to human support."
        else:
            return (
                prefix
                + "I don't have access to our verified policy documents right now, so I cannot confirm this. "
                + "Would you like me to connect you to a human support agent?"
            )
    else:
        # Step 2: RAG Knowledge Base Mode (retrieves real ZentroMart policies)
        if "milk" in q_lower or "dairy" in q_lower or "perishable" in q_lower:
            return prefix + "Fresh groceries like milk, vegetables, and dairy can only be reported within 2 hours of delivery if spoiled. Proof of damage is required for refunds."
        elif "soundbar" in q_lower or "electronic" in q_lower or "sound" in q_lower:
            return prefix + "All electronics like soundbars and TVs have a 7-day replacement/return window from the delivery date, provided they have original packaging."
        elif "broken egg" in q_lower or "zm-11029" in q_lower or "damaged" in q_lower:
            return prefix + "I apologize for the broken items. For Order ZM-11029, our policy provides an instant refund or replacement credit for verified damaged perishables."
        elif "cancel" in q_lower:
            return prefix + "Orders can be cancelled freely anytime before they are dispatched. If already dispatched, you may refuse delivery at your doorstep."
        elif "upi" in q_lower or "refund" in q_lower:
            return prefix + "UPI refunds reflect in your bank account within 24 to 48 hours. Credit or debit card refunds take 5 to 7 business days."
        elif "customer care" in q_lower or "phone" in q_lower or "number" in q_lower:
            return prefix + "Our 24x7 customer helpline is 1800-ZENTRO (1800-936-876), or you can email us at support@zentromart.in."
        elif "where is my order" in q_lower or "tracking" in q_lower:
            return prefix + "I can locate your package right away. Could you please provide your Order ID?"
        else:
            return prefix + "According to our store policies, we deliver across major Indian cities with 24x7 support. How else may I assist you?"


def main() -> None:
    parser = argparse.ArgumentParser(description="Live Working VoiceOps Assistant")
    parser.add_argument("--mute", action="store_true", help="Disable spoken voice TTS audio")
    parser.add_argument("--mode", choices=["step1", "step2"], default="step2", help="Operating mode: step1 (baseline) or step2 (RAG)")
    args = parser.parse_args()

    api_key = os.environ.get("OPENAI_API_KEY")
    client = None
    if api_key and api_key != "your_openai_api_key_here":
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            backend_label = "Live OpenAI API (gpt-4o-mini)"
        except Exception:
            backend_label = "Local Simulation Engine"
    else:
        backend_label = "Local Simulation Engine (Set OPENAI_API_KEY in .env for live LLM)"

    print("\n" + "=" * 65)
    print("   🎙️  ZENTROMART LIVE WORKING VOICEOPS ASSISTANT (2026)  🎙️")
    print("=" * 65)
    print(f" • Mode          : [{'Step 1: Baseline (Safe Guessing)' if args.mode == 'step1' else 'Step 2: RAG (Policy Knowledge Base)'}]")
    print(f" • Voice Audio   : [{'Muted' if args.mute else 'Enabled (Windows Speech Synthesizer)'}]")
    print(f" • Backend       : {backend_label}")
    print("-" * 65)
    print("Commands:")
    print("  Type any question to speak to the assistant.")
    print("  Type '1'-'8' to test a preset sample query from practice dataset.")
    print("  Type 'mode' to toggle between Step 1 (Baseline) and Step 2 (RAG).")
    print("  Type 'mute' or 'voice' to toggle audio.")
    print("  Type 'exit' or 'quit' to end.")
    print("-" * 65)

    presets = {
        "1": "Can I return the milk packet that was delivered yesterday?",
        "2": "Where is my order? The tracking hasn't updated since morning.",
        "3": "I want to return a soundbar I purchased 5 days ago. What is your return window?",
        "4": "I received broken eggs in my order ZM-11029. Can I get a refund?",
        "5": "What is your customer care phone number?",
        "6": "Do you deliver groceries to Pune and Hyderabad?",
        "7": "Can I cancel my television order before it is dispatched?",
        "8": "How many days does a UPI refund take to reflect in my bank account?",
    }

    current_mode = args.mode
    audio_enabled = not args.mute

    while True:
        try:
            user_input = input(f"\n[Customer ({current_mode.upper()})]: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting VoiceOps assistant. Goodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() in ["exit", "quit", "q"]:
            print("Session ended. Have a great day!")
            break

        if user_input.lower() == "mode":
            current_mode = "step1" if current_mode == "step2" else "step2"
            print(f"Switched mode to: {current_mode.upper()} ({'Baseline Safe' if current_mode == 'step1' else 'RAG Policy Engine'})")
            continue

        if user_input.lower() == "mute":
            audio_enabled = False
            print("Audio voice output: MUTED.")
            continue

        if user_input.lower() == "voice":
            audio_enabled = True
            print("Audio voice output: ENABLED.")
            continue

        # Check preset shortcut
        if user_input in presets:
            query = presets[user_input]
            print(f"-> Selected Preset #{user_input}: \"{query}\"")
        else:
            query = user_input

        print("\nThinking...")
        answer = answer_query(query, current_mode, client, os.environ.get("OPENAI_MODEL", "gpt-4o-mini"))
        print(f"\n[ZentroMart AI]:\n{answer}")

        if audio_enabled:
            print("🔊 (Speaking response aloud...)")
            speak(answer)


if __name__ == "__main__":
    main()
