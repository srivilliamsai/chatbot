# Software Engineering Assistant — Technical Documentation

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Backend Documentation](#2-backend-documentation)
3. [Frontend Documentation](#3-frontend-documentation)
4. [API Documentation](#4-api-documentation)
5. [Configuration Reference](#5-configuration-reference)
6. [Test Documentation](#6-test-documentation)
7. [Deployment Guide](#7-deployment-guide)

---

## 1. Architecture Overview

### System Architecture Diagram

```
+-----------------------------------------------------------------+
|                        USER (Browser)                           |
|                    http://localhost:8501                        |
+--------------------------+--------------------------------------+
                           |
                           |  HTTP / WebSocket
                           v
+-----------------------------------------------------------------+
|                    STREAMLIT SERVER                             |
|                       (app.py)                                  |
|  +-------------+  +--------------+  +--------------------+      |
|  |   UI Layer  |  | Session State|  |  Input Validation  |      |
|  |  (Frontend) |  |  Management  |  |     (utils.py)     |      |
|  |             |  |              |  |                    |      |
|  |  - CSS/HTML |  |  - Chat      |  |  - validate_input  |      |
|  |  - Chat     |  |    History   |  |  - estimate_tokens |      |
|  |    Messages |  |  - Config    |  |  - export_chat     |      |
|  |  - Sidebar  |  |    State     |  |                    |      |
|  +------+------+  +------+-------+  +--------+-----------+      |
|         |                |                   |                  |
|         +----------------+-------------------+                  |
|                          |                                      |
|                          v                                      |
|  +----------------------------------------------------------+   |
|  |                  LANGCHAIN PIPELINE                      |   |
|  |                                                          |   |
|  |  ChatPromptTemplate  ->  ChatOpenAI  ->  StrOutputParser |   |
|  |                                                          |   |
|  |  +---------------+   +------------+   +--------------+   |   |
|  |  | System Prompt |   |  LLM Call  |   | Parse String |   |   |
|  |  | Chat History  |-->|  (Model)   |-->|   Output     |   |   |
|  |  | User Input    |   |            |   |              |   |   |
|  |  +---------------+   +-----+------+   +--------------+   |   |
|  |                            |                             |   |
|  +----------------------------+-----------------------------+   |
|                               |                                 |
+-------------------------------+---------------------------------+
                                |
                                |  HTTPS (REST API)
                                v
+-----------------------------------------------------------------+
|                    OPENROUTER API                               |
|                https://openrouter.ai/api/v1                     |
|                                                                 |
|  Routes to selected model:                                      |
|  +-----------------+  +---------------+  +------------------+   |
|  | Gemini 2.5 Flash|  | Qwen 2.5 (7B) |  |   Gemma 2 (9B)   |   |
|  +-----------------+  +---------------+  +------------------+   |
+-----------------------------------------------------------------+
```

### Data Flow

```
User Input
    |
    v
Input Validation (utils.py)
    |
    v (if valid)
Build Prompt (config.py SYSTEM_PROMPT + chat_history + user input)
    |
    v
LangChain Chain (ChatPromptTemplate -> ChatOpenAI -> StrOutputParser)
    |
    v
OpenRouter API -> Selected Model (Gemini / Qwen / Gemma)
    |
    v
Response String
    |
    v
Display in Chat UI + Append to Session State
```

### Component Diagram

```
+--------------------------------------------------+
|                   app.py                         |
|  (Main Application - UI + Orchestration)         |
+--------------------------------------------------+
|  Imports:                                        |
|  +------------+  +----------+  +--------------+  |
|  | config.py  |  | utils.py |  | LangChain    |  |
|  |            |  |          |  | + OpenRouter |  |
|  | - MODELS   |  | - export |  |              |  |
|  | - PROMPTS  |  | - tokens |  | - ChatOpenAI |  |
|  | - SETTINGS |  | - valid. |  | - Templates  |  |
|  +------------+  +----------+  +--------------+  |
+--------------------------------------------------+
```

---

## 2. Backend Documentation

### 2.1 LangChain Pipeline (`app.py`)

The backend uses a standard LangChain LCEL (LangChain Expression Language) chain:

```python
chain = prompt | llm | StrOutputParser()
```

**Components:**

| Component | Type | Purpose |
|-----------|------|---------|
| `prompt` | `ChatPromptTemplate` | Assembles system prompt, chat history, and user input |
| `llm` | `ChatOpenAI` | LLM client configured for OpenRouter |
| `StrOutputParser` | Parser | Extracts raw string from LLM response |

### 2.2 Model Management

Models are defined in `config.py` and loaded via `@st.cache_resource`:

```python
@st.cache_resource
def get_llm(model_key: str, temp: float):
    return ChatOpenAI(
        model=MODELS[model_key],
        openai_api_key=OPENROUTER_API_KEY,
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=temp,
        max_tokens=MAX_TOKENS,
    )
```

The `@st.cache_resource` decorator ensures the LLM client is created once and reused across reruns, avoiding unnecessary re-initialization.

### 2.3 Session State

Streamlit's `st.session_state` stores the conversation:

```python
st.session_state.chat_history = [
    HumanMessage(content="..."),
    AIMessage(content="..."),
    ...
]
```

Context window is limited to the last `MAX_CONTEXT_MESSAGES` (20) messages when sending to the LLM.

### 2.4 Prompt Engineering (`config.py`)

The system prompt enforces:

| Aspect | Implementation |
|--------|----------------|
| **Role** | "Expert Software Engineer and Architect" |
| **Domain** | Software engineering, programming, architecture, debugging, git, CS concepts |
| **Tone** | Professional, direct, encouraging, technically precise |
| **Refusal** | Template response redirecting user for out-of-domain queries |
| **Structure** | Analysis → Solution → Best Practices → Disclaimer |
| **Flexibility** | Simple questions get concise answers; complex ones get full structure |

### 2.5 Utilities (`utils.py`)

| Function | Purpose | Input | Output |
|----------|---------|-------|--------|
| `estimate_tokens(text)` | Rough token count estimation | `str` | `int` |
| `export_chat_as_markdown(history)` | Export chat to Markdown | `list[Message]` | `str` |
| `export_chat_as_json(history)` | Export chat to JSON | `list[Message]` | `str` |
| `validate_input(text)` | Validate user input | `str` | `tuple[bool, str]` |

---

## 3. Frontend Documentation

### 3.1 Design System

The UI follows Apple's Human Interface Guidelines with a dark theme:

| Token | Value | Usage |
|-------|-------|-------|
| `--bg-primary` | `#000000` | Main background |
| `--bg-secondary` | `#1c1c1e` | Cards, sidebar |
| `--bg-tertiary` | `#2c2c2e` | Code blocks, inputs |
| `--text-primary` | `#f5f5f7` | Headings, main text |
| `--text-secondary` | `#a1a1a6` | Body text |
| `--text-tertiary` | `#6e6e73` | Labels, hints |
| `--accent` | `#0a84ff` | Interactive elements |
| `--border` | `rgba(255,255,255,0.08)` | Borders, dividers |
| `--radius-sm/md/lg` | `8/12/16px` | Corner rounding |

### 3.2 Typography

- **Font**: Inter (Google Fonts) — matches Apple's SF Pro aesthetic
- **Headings**: 700 weight, letter-spacing -0.02em
- **Body**: 400 weight, line-height 1.6
- **Code**: SF Mono / Fira Code / Menlo monospace stack

### 3.3 Layout Structure

```
+---------------------------------------------------------+
| +----------+  +--------------------------------------+  |
| |          |  |                                      |  |
| | SIDEBAR  |  |            MAIN CONTENT              |  |
| |          |  |                                      |  |
| | - Model  |  |  +------------------------------+    |  |
| | - Temp   |  |  |       Welcome Card           |    |  |
| | - Caps   |  |  |   (shown when no history)    |    |  |
| | - Stats  |  |  |                              |    |  |
| | - Export |  |  |  +------+ +------+           |    |  |
| | - Clear  |  |  |  | Ex 1 | | Ex 2 |           |    |  |
| |          |  |  |  +------+ +------+           |    |  |
| |          |  |  |  +------+ +------+           |    |  |
| |          |  |  |  | Ex 3 | | Ex 4 |           |    |  |
| |          |  |  |  +------+ +------+           |    |  |
| |          |  |  +------------------------------+    |  |
| |          |  |                                      |  |
| |          |  |  +------------------------------+    |  |
| |          |  |  |  Chat Messages (scrollable)  |    |  |
| |          |  |  +------------------------------+    |  |
| |          |  |                                      |  |
| |          |  |  +------------------------------+    |  |
| |          |  |  |  Chat Input (fixed bottom)   |    |  |
| |          |  |  +------------------------------+    |  |
| +----------+  +--------------------------------------+  |
+---------------------------------------------------------+
```

### 3.4 Responsive Design

| Breakpoint | Changes |
|------------|---------|
| > 768px | Full layout with sidebar, max-width 880px |
| <= 768px | Sidebar collapses, single-column examples, adjusted padding |

### 3.5 Sidebar Components

| Component | Type | Purpose |
|-----------|------|---------|
| Model Selector | `st.selectbox` | Switch between AI models |
| Temperature Slider | `st.slider` | Control response randomness (0.0–1.0) |
| Capabilities | Static text | List of supported topics |
| Session Stats | Dynamic text | Message count + estimated tokens |
| Export Button | `st.download_button` | Download chat as Markdown |
| Clear Button | `st.button` | Reset conversation history |

---

## 4. API Documentation

### 4.1 External API: OpenRouter

The application communicates with OpenRouter's OpenAI-compatible API.

**Endpoint:** `https://openrouter.ai/api/v1/chat/completions`

**Authentication:** Bearer token via `OPENROUTER_API_KEY`

**Request Format (sent by LangChain):**

```json
{
  "model": "google/gemini-2.5-flash",
  "messages": [
    {"role": "system", "content": "<SYSTEM_PROMPT>"},
    {"role": "user", "content": "How does git rebase work?"},
    {"role": "assistant", "content": "...previous response..."},
    {"role": "user", "content": "Can you show an example?"}
  ],
  "temperature": 0.2,
  "max_tokens": 4096
}
```

**Response Format:**

```json
{
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "### Analysis\n..."
      }
    }
  ],
  "usage": {
    "prompt_tokens": 250,
    "completion_tokens": 800,
    "total_tokens": 1050
  }
}
```

### 4.2 Available Models

| Display Name | Model ID | Provider | Cost |
|-------------|----------|----------|------|
| Gemini 2.5 Flash | `google/gemini-2.5-flash` | Google | Free |
| Qwen 2.5 (7B) | `qwen/qwen-2.5-7b-instruct:free` | Alibaba | Free |
| Gemma 2 (9B) | `google/gemma-2-9b-it:free` | Google | Free |

### 4.3 Internal Function API

#### `config.py`

| Export | Type | Description |
|--------|------|-------------|
| `MODELS` | `dict[str, str]` | Model display name → OpenRouter model ID |
| `DEFAULT_MODEL` | `str` | Default model key |
| `SYSTEM_PROMPT` | `str` | System prompt for LLM |
| `EXAMPLE_PROMPTS` | `list[str]` | Welcome screen example queries |
| `APP_TITLE` | `str` | Application title |
| `APP_DESCRIPTION` | `str` | Application subtitle |
| `MAX_CONTEXT_MESSAGES` | `int` | Max messages sent as context (20) |
| `DEFAULT_TEMPERATURE` | `float` | Default temperature (0.2) |
| `MAX_TOKENS` | `int` | Max response tokens (4096) |

#### `utils.py`

| Function | Signature | Returns |
|----------|-----------|---------|
| `estimate_tokens` | `(text: str) → int` | Estimated token count |
| `export_chat_as_markdown` | `(chat_history: list) → str` | Markdown string |
| `export_chat_as_json` | `(chat_history: list) → str` | JSON string |
| `validate_input` | `(text: str) → tuple[bool, str]` | Validity + error message |

---

## 5. Configuration Reference

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENROUTER_API_KEY` | Yes | API key from openrouter.ai |

### Application Settings (`config.py`)

| Setting | Default | Range | Description |
|---------|---------|-------|-------------|
| `DEFAULT_TEMPERATURE` | `0.2` | 0.0–1.0 | Response randomness |
| `MAX_TOKENS` | `4096` | 1–128000 | Max response length |
| `MAX_CONTEXT_MESSAGES` | `20` | 1–100 | Messages sent as context |

---

## 6. Test Documentation

### Test Summary

| Test Class | Tests | Category |
|------------|-------|----------|
| `TestConfig` | 12 | Configuration validation |
| `TestEstimateTokens` | 5 | Token estimation |
| `TestValidateInput` | 8 | Input validation |
| `TestExportChatMarkdown` | 4 | Markdown export |
| `TestExportChatJSON` | 3 | JSON export |
| `TestDomainBoundaryScenarios` | 14 | Domain boundary (10 in + 4 out) |
| `TestLLMChainSetup` | 3 | LangChain integration |
| `TestEdgeCases` | 5 | Edge cases |
| **Total** | **54** | |

### Running Tests

```bash
# All tests
python -m pytest tests.py -v

# Specific class
python -m pytest tests.py::TestValidateInput -v

# With coverage (requires pytest-cov)
python -m pytest tests.py --cov=. --cov-report=term-missing
```

### Test Scenarios Detail

#### In-Domain Queries (10 scenarios — should be answered)

| # | Query | Topic |
|---|-------|-------|
| 1 | What is the difference between an Abstract Class and an Interface in Java? | OOP Concepts |
| 2 | How do I resolve a merge conflict in Git? | Version Control |
| 3 | Explain the MVC architecture pattern. | Architecture Patterns |
| 4 | What are the SOLID principles of object-oriented design? | Design Principles |
| 5 | Can you explain how a Docker container differs from a Virtual Machine? | DevOps / Containers |
| 6 | How does a hash map work internally in Python? | Data Structures |
| 7 | What is the time complexity of quicksort? | Algorithms |
| 8 | How do I write a REST API using FastAPI? | Web Development |
| 9 | Explain dependency injection with an example. | Design Patterns |
| 10 | What is CI/CD and why is it important? | DevOps Practices |

#### Out-of-Domain Queries (4 scenarios — should be refused)

| # | Query | Topic | Expected Response |
|---|-------|-------|------------------|
| 1 | What is the capital of Australia? | Geography | Refusal + redirect |
| 2 | Can you give me a recipe for chocolate chip cookies? | Cooking | Refusal + redirect |
| 3 | How do I treat a mild sunburn? | Medical Advice | Refusal + redirect |
| 4 | What is the best investment strategy for 2026? | Financial Advice | Refusal + redirect |

---

## 7. Deployment Guide

### Streamlit Community Cloud (Recommended)

**Steps:**

1. Push your code to GitHub (ensure `.env` is in `.gitignore`)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click "New app"
4. Select your repository, branch, and `app.py`
5. Go to Settings → Secrets and add:
   ```
   OPENROUTER_API_KEY = "sk-or-v1-..."
   ```
6. Click "Deploy"

**Requirements:**
- Public or private GitHub repository
- `requirements.txt` at root level
- No `.env` file needed (secrets managed by Streamlit)

### File Checklist for Deployment

| File | Required | Purpose |
|------|----------|---------|
| `app.py` | Yes | Main application |
| `config.py` | Yes | Configuration |
| `utils.py` | Yes | Utilities |
| `requirements.txt` | Yes | Dependencies |
| `.env` | No | Local only (use Streamlit Secrets in cloud) |
| `tests.py` | No | Not needed in production |
