# Data Dictionary - Capstone Project FTTT 2026

## Dataset: `practice/questions.csv`

| Column Name | Type | Description |
|---|---|---|
| `question_id` | String | Unique 3-digit identifier for the test question (preserves leading zeros, e.g., `001`). |
| `question` | String | The clean text representation of the customer query. |
| `asr_text` | String | Simulated automatic speech recognition (ASR) transcription of the user's spoken voice query. |
| `order_id` | String | Associated order number if applicable (e.g., `ZM-11029`). |
| `category` | String | Domain category of the query (e.g., `Groceries`, `Electronics`, `Refunds`, `General`). |
| `expected_decision` | String | The gold standard ground-truth policy decision or expected action for evaluation. |
