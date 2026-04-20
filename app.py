import os
import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser

from config import (
    MODELS, DEFAULT_MODEL, APP_TITLE, APP_DESCRIPTION,
    MAX_CONTEXT_MESSAGES, DEFAULT_TEMPERATURE, MAX_TOKENS,
    SYSTEM_PROMPT, EXAMPLE_PROMPTS
)
from utils import estimate_tokens, export_chat_as_markdown, validate_input

# --- Configuration ---
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    st.error("OPENROUTER_API_KEY not found. Please check your .env file.")
    st.stop()

# --- Page Config ---
st.set_page_config(
    page_title=APP_TITLE,
    page_icon="",
    layout="wide",
    initial_sidebar_state="auto"
)

# --- Apple-Style CSS ---
st.markdown("""
<style>
    /* --- Import SF-style font --- */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* --- Root variables --- */
    :root {
        --bg-primary: #000000;
        --bg-secondary: #1c1c1e;
        --bg-tertiary: #2c2c2e;
        --bg-elevated: #1c1c1e;
        --text-primary: #f5f5f7;
        --text-secondary: #a1a1a6;
        --text-tertiary: #6e6e73;
        --accent: #0a84ff;
        --accent-hover: #409cff;
        --border: rgba(255, 255, 255, 0.08);
        --border-focus: rgba(10, 132, 255, 0.4);
        --radius-sm: 8px;
        --radius-md: 12px;
        --radius-lg: 16px;
        --shadow-sm: 0 1px 3px rgba(0,0,0,0.3);
        --shadow-md: 0 4px 12px rgba(0,0,0,0.4);
        --transition: all 0.2s ease;
    }

    /* --- Global --- */
    .stApp {
        background-color: var(--bg-primary) !important;
        color: var(--text-primary) !important;
    }

    /* Safely hide the deploy button and footer without breaking icons */
    .stDeployButton {
        display: none !important;
    }
    
    footer {
        visibility: hidden !important;
    }
    
    /* Keep header transparent but don't mess with its visibility */
    [data-testid="stHeader"] {
        background: transparent !important;
    }

    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 4rem !important;
        max-width: 880px !important;
    }
    
    /* --- Fix Bottom Chat Background --- */
    [data-testid="stBottomBlockContainer"], 
    [data-testid="stBottom"] > div {
        background-color: var(--bg-primary) !important;
        background: var(--bg-primary) !important;
    }

    /* --- Typography --- */
    h1 {
        font-family: 'Inter', sans-serif !important;
        font-weight: 700 !important;
        font-size: 2rem !important;
        color: var(--text-primary) !important;
        letter-spacing: -0.02em !important;
        margin-bottom: 0 !important;
    }

    h2, h3 {
        font-family: 'Inter', sans-serif !important;
        color: var(--text-primary) !important;
        letter-spacing: -0.01em !important;
    }

    p, li {
        font-family: 'Inter', sans-serif !important;
        color: var(--text-secondary) !important;
        line-height: 1.6 !important;
    }

    /* --- Sidebar --- */
    section[data-testid="stSidebar"] {
        background-color: var(--bg-secondary) !important;
        border-right: 1px solid var(--border) !important;
    }

    section[data-testid="stSidebar"] .block-container {
        padding-top: 2rem !important;
    }

    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        color: var(--text-tertiary) !important;
        margin-bottom: 0.5rem !important;
    }

    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] li {
        font-size: 0.9rem !important;
        color: var(--text-secondary) !important;
    }

    /* --- Slider --- */
    .stSlider > div > div > div > div {
        background-color: var(--accent) !important;
    }

    /* --- Buttons --- */
    .stButton > button {
        background-color: var(--bg-tertiary) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-sm) !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
        font-size: 0.875rem !important;
        padding: 0.5rem 1rem !important;
        transition: var(--transition) !important;
        width: 100% !important;
    }

    .stButton > button:hover {
        background-color: var(--bg-elevated) !important;
        border-color: var(--border-focus) !important;
        color: var(--accent) !important;
    }

    /* --- Select Box --- */
    .stSelectbox > div > div {
        background-color: var(--bg-tertiary) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-sm) !important;
        color: var(--text-primary) !important;
    }

    /* --- Chat Messages --- */
    .stChatMessage {
        background-color: transparent !important;
        border: none !important;
        padding: 1rem 0 !important;
    }

    [data-testid="stChatMessageContent"] {
        font-family: 'Inter', sans-serif !important;
        font-size: 0.95rem !important;
        line-height: 1.7 !important;
        color: var(--text-primary) !important;
    }

    [data-testid="stChatMessageContent"] p {
        color: var(--text-primary) !important;
    }

    /* Code blocks inside chat */
    [data-testid="stChatMessageContent"] pre {
        background-color: var(--bg-tertiary) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-md) !important;
        padding: 1rem !important;
    }

    [data-testid="stChatMessageContent"] code {
        font-family: 'SF Mono', 'Fira Code', 'Menlo', monospace !important;
        font-size: 0.85rem !important;
    }

    /* Inline code */
    [data-testid="stChatMessageContent"] p code {
        background-color: var(--bg-tertiary) !important;
        padding: 2px 6px !important;
        border-radius: 4px !important;
        font-size: 0.85rem !important;
    }

    /* --- Chat Input --- */
    .stChatInput {
        border-color: var(--border) !important;
    }

    .stChatInput > div {
        background-color: var(--bg-secondary) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-lg) !important;
    }

    .stChatInput textarea {
        color: var(--text-primary) !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* --- Divider --- */
    hr {
        border-color: var(--border) !important;
        margin: 1rem 0 !important;
    }

    /* --- Spinner --- */
    .stSpinner > div {
        border-top-color: var(--accent) !important;
    }

    /* --- Welcome Card --- */
    .welcome-card {
        background: var(--bg-secondary);
        border: 1px solid var(--border);
        border-radius: var(--radius-lg);
        padding: 2.5rem;
        margin: 2rem 0;
        text-align: center;
    }

    .welcome-card h2 {
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        color: var(--text-primary) !important;
        margin-bottom: 0.5rem !important;
        letter-spacing: -0.02em !important;
    }

    .welcome-card p {
        color: var(--text-tertiary) !important;
        font-size: 0.95rem !important;
        margin-bottom: 1.5rem !important;
    }

    /* --- Example Prompt Buttons --- */
    .example-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 0.75rem;
        margin-top: 1rem;
    }

    .example-btn {
        background: var(--bg-tertiary);
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        padding: 0.85rem 1rem;
        text-align: left;
        font-family: 'Inter', sans-serif;
        font-size: 0.85rem;
        color: var(--text-secondary);
        cursor: pointer;
        transition: var(--transition);
        text-decoration: none;
        display: block;
    }

    .example-btn:hover {
        border-color: var(--border-focus);
        color: var(--text-primary);
        background: rgba(10, 132, 255, 0.06);
    }

    /* --- Stats Bar --- */
    .stats-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.6rem 1rem;
        background: var(--bg-secondary);
        border: 1px solid var(--border);
        border-radius: var(--radius-sm);
        margin-top: 0.75rem;
        font-size: 0.8rem;
        color: var(--text-tertiary);
        font-family: 'Inter', sans-serif;
    }

    .stats-bar span {
        color: var(--text-tertiary) !important;
        font-size: 0.8rem !important;
    }

    /* --- Download button --- */
    .stDownloadButton > button {
        background-color: var(--bg-tertiary) !important;
        color: var(--text-secondary) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-sm) !important;
        font-size: 0.8rem !important;
        font-weight: 500 !important;
        transition: var(--transition) !important;
    }

    .stDownloadButton > button:hover {
        border-color: var(--border-focus) !important;
        color: var(--accent) !important;
    }

    /* --- Mobile --- */
    @media (max-width: 768px) {
        .block-container {
            padding: 1rem !important;
            max-width: 100% !important;
        }

        h1 {
            font-size: 1.5rem !important;
        }

        .welcome-card {
            padding: 1.5rem;
        }

        .example-grid {
            grid-template-columns: 1fr;
        }

        .stChatInputContainer {
            padding-bottom: 4rem !important;
        }
    }
</style>
""", unsafe_allow_html=True)


# --- Sidebar ---
with st.sidebar:
    st.markdown("### Configuration")

    selected_model = st.selectbox(
        "Model",
        options=list(MODELS.keys()),
        index=list(MODELS.keys()).index(DEFAULT_MODEL),
        help="Select the AI model to power responses."
    )

    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=DEFAULT_TEMPERATURE,
        step=0.1,
        help="Lower = more focused. Higher = more creative."
    )

    st.markdown("---")

    st.markdown("### Capabilities")
    st.markdown(
        "Code review and debugging\n\n"
        "System architecture design\n\n"
        "Best practices and patterns\n\n"
        "Git and version control"
    )

    st.markdown("---")

    # Chat stats
    msg_count = len(st.session_state.get("chat_history", []))
    total_tokens = sum(
        estimate_tokens(m.content)
        for m in st.session_state.get("chat_history", [])
    )
    st.markdown(f"### Session")
    st.markdown(f"Messages: {msg_count}  \nTokens (est.): {total_tokens:,}")

    st.markdown("---")

    # Export
    if msg_count > 0:
        md_export = export_chat_as_markdown(
            st.session_state.get("chat_history", [])
        )
        st.download_button(
            "Export Chat",
            data=md_export,
            file_name="chat_export.md",
            mime="text/markdown"
        )

    # Reset
    if st.button("Clear Conversation"):
        st.session_state.chat_history = []
        st.rerun()


# --- LLM Init ---
@st.cache_resource
def get_llm(model_key: str, temp: float):
    """Initialize the LangChain LLM with the selected model."""
    return ChatOpenAI(
        model=MODELS[model_key],
        openai_api_key=OPENROUTER_API_KEY,
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=temp,
        max_tokens=MAX_TOKENS,
    )


llm = get_llm(selected_model, temperature)

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("placeholder", "{chat_history}"),
    ("user", "{input}")
])

chain = prompt | llm | StrOutputParser()


# --- Session State ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# --- Header ---
st.title(APP_TITLE)


# --- Welcome Screen or Chat ---
if not st.session_state.chat_history:
    st.write("")
    st.write("")
    with st.container(border=True):
        st.markdown(f"<h2 style='text-align: center; margin-bottom: 0.2rem;'>{APP_TITLE}</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; color: #a1a1a6; margin-bottom: 1.5rem;'>{APP_DESCRIPTION}</p>", unsafe_allow_html=True)
        
        cols = st.columns(2)
        for i, p in enumerate(EXAMPLE_PROMPTS):
            if cols[i % 2].button(p, key=f"ex_btn_{i}", use_container_width=True):
                st.session_state.example_clicked = p
                st.rerun()
else:
    # Display chat history
    for message in st.session_state.chat_history:
        if isinstance(message, HumanMessage):
            with st.chat_message("user"):
                st.markdown(message.content)
        elif isinstance(message, AIMessage):
            with st.chat_message("assistant"):
                st.markdown(message.content)


# --- Chat Input & Logic ---
user_query = st.chat_input("Ask a software engineering question...")

# Did the user click an example button instead?
if st.session_state.get("example_clicked"):
    user_query = st.session_state.example_clicked
    st.session_state.example_clicked = None  # Reset it so it doesn't loop

if user_query:
    is_valid, error_msg = validate_input(user_query)

    if not is_valid:
        st.error(error_msg)
    else:
        with st.chat_message("user"):
            st.markdown(user_query)

        with st.chat_message("assistant"):
            with st.spinner(""):
                try:
                    response = chain.invoke({
                        "chat_history": st.session_state.chat_history[
                            -MAX_CONTEXT_MESSAGES:
                        ],
                        "input": user_query
                    })
                    st.markdown(response)

                    st.session_state.chat_history.append(
                        HumanMessage(content=user_query)
                    )
                    st.session_state.chat_history.append(
                        AIMessage(content=response)
                    )
                except Exception as e:
                    st.error(f"Something went wrong. Please try again.\n\n{str(e)}")
