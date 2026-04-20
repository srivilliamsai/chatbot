# Software Engineering Domain LLM Assistant

A domain-focused AI assistant built with OpenRouter, LangChain, and Streamlit. It answers software engineering questions with structured, professional responses and refuses out-of-domain queries.

---

## Features

- **Domain-specific intelligence** — answers only software engineering queries
- **Multiple model support** — switch between Gemini, DeepSeek, and Llama models
- **Clean Apple-style UI** — dark theme, Inter font, minimal layout
- **Structured responses** — Analysis, Solution, Best Practices, Disclaimer
- **Chat export** — download conversation as Markdown
- **Input validation** — character limits and sanitization
- **Configurable temperature** — control response creativity
- **Session statistics** — track messages and estimated token usage

---

## Project Structure

```
SRM Assigment/
├── app.py              # Main Streamlit application
├── config.py           # Centralized configuration (models, prompts, settings)
├── utils.py            # Utility functions (export, validation, tokens)
├── tests.py            # Test suite (54 tests)
├── requirements.txt    # Python dependencies
├── .env                # API key (not committed)
├── .gitignore          # Git ignore rules
├── explanation.md      # Prompt engineering explanation
├── test_queries_and_outputs.md  # Manual test records
└── README.md           # This file
```

---

## Requirements Checklist

- [x] OpenRouter API for LLM access
- [x] LangChain for prompt templates and orchestration
- [x] Explicit role definition and domain boundaries
- [x] Structured output format
- [x] Mandatory disclaimer and refusal behavior
- [x] 14 test scenarios (10 in-domain + 4 out-of-domain)
- [x] UI implementation via Streamlit
- [x] 54 automated unit tests

---

## Setup

### Prerequisites

- Python 3.9+
- An OpenRouter API key ([get one here](https://openrouter.ai/keys))

### Installation

```bash
# Clone the repository
git clone <repo-url>
cd "SRM Assigment"

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the project root:

```
OPENROUTER_API_KEY=your_key_here
```

### Run Locally

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501/`

### Run Tests

```bash
python -m pytest tests.py -v
```

---

## Deployment (Streamlit Community Cloud)

1. Push code to a GitHub repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account
4. Select the repository and `app.py` as the main file
5. Add your API key in **Settings > Secrets**:
   ```
   OPENROUTER_API_KEY = "your_key_here"
   ```
6. Deploy

---

## Testing

The project includes 54 automated tests across 8 test classes. Run with:

```bash
python -m pytest tests.py -v
```

See `test_queries_and_outputs.md` for manual test records with full LLM responses.
