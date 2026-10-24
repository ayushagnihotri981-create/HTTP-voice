# VoiceOps 2026 - Live Working Voice Operations System
## ZentroMart Customer Support Voice & Text Operations

An end-to-end working voice and text customer support operations suite for **ZentroMart**, an online grocery and electronics store in India.

---

## 📁 Directory Structure

```
live working voice ops/
├── live_voiceops.py             # 🎙️ Interactive Live Assistant (Terminal + Spoken Voice Audio)
├── run_live.bat                 # 🚀 One-click Windows double-clickable launcher
├── step1_baseline.py            # Step 1 Baseline Evaluation Runner
├── grade_step1.py               # Step 1 Evaluation Grader & Scorecard generator
├── policies/
│   └── zentromart_policies.md   # Official store policies (Groceries, Electronics, UPI Refunds)
├── practice/
│   └── questions.csv            # Test inquiries (Speech ASR inputs, order IDs, ground truth)
├── outputs/
│   └── step1/
│       ├── step1_answers.csv    # Evaluated model responses
│       └── step1_scorecard.csv  # Graded scorecard
├── requirements.txt             # Project dependencies (openai, pandas, python-dotenv)
├── .env.example                 # Template for API keys
├── DATA_DICTIONARY.md           # Dataset schema specification
└── README.md                    # This documentation file
```

---

## 🚀 How to Run

### 1. Launch Interactive Live VoiceOps Assistant
Double-click `run_live.bat` or run in terminal:
```powershell
& "C:\Users\ASHUTOSH\AppData\Local\Programs\Python\Python311\python.exe" live_voiceops.py
```

**Assistant Features:**
- **Live Spoken Audio**: Answers are spoken aloud using Windows Speech Synthesizer.
- **Quick Test Presets**: Type numbers `1` through `8` to test any practice query instantly.
- **Mode Toggle**: Type `mode` to switch between:
  - **Step 1 (Safe Baseline)**: Declines guessing unknown policies and offers human handoff.
  - **Step 2 (RAG Knowledge Engine)**: Answers policy queries directly using `policies/zentromart_policies.md`.
- **Audio Controls**: Type `mute` or `voice` to toggle spoken audio.

---

### 2. Run Step 1 Automated Evaluation
```powershell
& "C:\Users\ASHUTOSH\AppData\Local\Programs\Python\Python311\python.exe" step1_baseline.py --questions practice/questions.csv
```

### 3. Run Graded Scorecard
```powershell
& "C:\Users\ASHUTOSH\AppData\Local\Programs\Python\Python311\python.exe" grade_step1.py
```

---

### 4. Enable Live OpenAI API (Optional)
Copy `.env.example` to `.env` and insert your key:
```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```
*(If no API key is specified, both the live assistant and baseline evaluation run in safe simulation mode).*
