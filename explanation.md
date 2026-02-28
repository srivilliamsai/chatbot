# Software Engineering LLM Assistant - Project Explanation

## 1. Domain Scope
The domain chosen for this specialized AI assistant is **Software Engineering**. 

**Scope Definition:**
The assistant strictly answers questions related to programming, computer science concepts, system architecture, database design, git version control, Docker, and debugging. Its primary functions include explaining code snippets, providing boilerplate code, suggesting architectural choices, and outlining software development best practices.

**Out-of-Scope (What it will NOT answer):**
The assistant will immediately refuse to answer questions regarding medical advice, financial consulting, fitness regimens, recipes, subjective philosophical questions, general history, or any casual conversational queries not tethered to technology.

## 2. Prompt Design Strategy
The application employs LangChain (`ChatPromptTemplate`) to enforce rigid boundaries on the underlying LLM (via OpenRouter). The System Prompt was engineered with the following explicit criteria:

*   **Role Definition:** Starts by explicitly assigning the persona of an "Expert Software Engineer and Architect."
*   **Domain Boundaries:** Reinforces that the LLM ONLY functions within software engineering.
*   **Tone Control:** Instructs the LLM to remain "Professional, direct, encouraging, and technically precise," avoiding overly casual banter.
*   **Refusal Behavior (Safety):** The most critical part of the prompt is the explicit instruction on handling out-of-bounds queries. It uses a template response: *"I am a specialized Software Engineering assistant. I cannot provide information on [Topic]. Please ask me a question related to software development... "* This ensures a graceful, safe redirect rather than standard hallucination.
*   **Mandatory Output Structure:** The prompt forces the LLM to segment its response into predefined headers: 
    1. Analysis
    2. Solution / Explanation
    3. Best Practices
    4. Mandatory Disclaimer
*   **Mandatory Disclaimer:** The prompt ensures every generated response includes a standardized footer reminding the user to test code before pushing to production.

## 3. Limitations Observed
While the prompt engineering is robust, a few limitations persist with domain-specific LLM implementations:
*   **Fuzzy Boundaries:** Edge cases like asking, *"What is the financial cost of deploying this cloud architecture?"* straddle the line between Software Engineering and Finance. The LLM might occasionally struggle with whether to accept or refuse these border queries.
*   **Over-Segmentation:** For extremely simple questions (e.g., "What does `git pull` do?"), the mandatory output structure (Analysis, Solution, Best Practices) can feel slightly overly formal and bloated compared to a straightforward one-sentence answer.
*   **Latency:** Utilizing LangChain sequentially with the Streamlit UI and OpenRouter's API can introduce minor latency in response generation, depending on the dynamic model routing (e.g., using `openrouter/auto`). 
*   **Hallucination Risk within Domain:** While it refuses out-of-domain queries successfully, within the domain of Software Engineering it might confidently explain a deprecated library feature or propose a non-existent API attribute if pushed. The disclaimer mitigates liability, but not accuracy.
