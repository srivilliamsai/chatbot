# Software Engineering Domain LLM Assistant

A domain-focused AI assistant built with OpenRouter, LangChain, and Streamlit. It answers software engineering questions with structured, professional responses and refuses out-of-domain queries.

---

## 1. Chosen Vertical
**Vertical:** Software Engineering & Computer Science

This assistant is strictly bounded to the domain of software engineering. It acts as an expert Software Engineer and Architect, capable of answering questions related to programming languages, system architecture, debugging, version control (Git), and data structures/algorithms.

## 2. Approach and Logic
The core logic of the assistant is driven by a highly constrained System Prompt mapped to a LangChain pipeline, which sets explicit behavioral boundaries:

- **Strict Domain Filtering:** The prompt explicitly instructs the LLM to identify out-of-domain queries (e.g., medical advice, recipes, financial guidance). If a query falls outside the Software Engineering vertical, the LLM refuses to answer and redirects the user with a standardized message.
- **Structured Output Strategy:** For complex questions, the LLM is prompted to return answers strictly in a structured format: `Analysis -> Solution -> Best Practices -> Disclaimer`. This guarantees professional, consistent readability.
- **Modular Extensibility:** Instead of hardcoding API calls, the logic uses `LangChain Expression Language (LCEL)`. The pipeline (`prompt | llm | parser`) cleanly separates the prompt engineering from the model invocation.
- **Model Agnosticism:** By utilizing OpenRouter's API, the system seamlessly routes queries to different foundational models (e.g., Gemini, Qwen, Gemma) allowing for easy comparison without changing the underlying code.

## 3. How the Solution Works
1. **Input Stage:** The user submits a query through the Streamlit web interface.
2. **Validation:** `utils.py` validates the input to ensure it meets length requirements and isn't empty.
3. **Context Assembly:** The input is passed to the LangChain `ChatPromptTemplate`, which merges the user's query with the strict `SYSTEM_PROMPT` (defined in `config.py`) and up to 20 messages of prior `chat_history`.
4. **Execution:** The initialized LLM (`ChatOpenAI` configured for OpenRouter) connects to the selected external model and processes the assembled context.
5. **Output Stage:** The response string is parsed, rendered as Markdown on the Apple-style dark theme UI, and automatically appended to the Streamlit session state history.

## 4. Assumptions Made
- **API Availability:** Assumes that the OpenRouter API endpoints and selected free-tier models remain active and stable.
- **Context Limits:** Assumes that maintaining a rolling history of the last 20 messages is sufficient for continuous conversation flow without exceeding standard token window limits.
- **User Intent:** Assumes the user interacts in English and expects technical output formatted in Markdown, complete with syntax-highlighted code blocks.
- **Local Environment:** Assumes the host environment supports Python 3.9+ and can run local Streamlit servers without port binding conflicts on port `8501`.

---

## Features

- **Domain-specific intelligence** — answers only software engineering queries
- **Multiple model support** — switch between Gemini, Qwen, and Gemma models
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
