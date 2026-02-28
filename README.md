# Software Engineering Domain LLM Assistant

This is a domain-focused AI assistant built using the OpenRouter API, LangChain, and Streamlit. It strictly answers questions related to Software Engineering and refuses out-of-domain queries.

## Requirements Checklist Completed
- [x] OpenRouter API for LLM Access
- [x] LangChain for prompt templates / orchestration
- [x] Explicit role definition & Domain boundaries
- [x] Structured output format
- [x] Mandatory disclaimer & Refusal behavior
- [x] At least 10 test queries (saved in `test_queries_and_outputs.md`)
- [x] UI implementation via Streamlit

## Setup Instructions

1. **Prerequisites**
   Must have Python 3.8+ installed.

2. **Run the Initialization Setup**
   The project has a virtual environment. If running from scratch:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Verify API Key**
   Ensure an `.env` file exists in the root directory containing your API key:
   ```
   OPENROUTER_API_KEY=your_key_here
   ```

4. **Run the Application**
   ```bash
   streamlit run app.py
   ```
   The application will automatically open in your default browser at `http://localhost:8501/`.

## Testing
To view the output of the mandatory 10 test queries (including 2 rejections), open the `test_queries_and_outputs.md` file.
