import os
import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser

# 1. Configuration & Setup
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    st.error("Error: OPENROUTER_API_KEY not found in environment variables. Please check your .env file.")
    st.stop()

# 2. UI Configuration
st.set_page_config(
    page_title="Software Engineering Assistant",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="auto"
)

# Custom CSS for Mobile Responsiveness and UI Polish
st.markdown("""
<style>
    /* Base adjustments for smaller screens */
    @media (max-width: 768px) {
        /* Make chat avatars scale better */
        .stChatMessage {
            padding: 1rem !important;
        }
        
        /* Adjust title size for mobile */
        h1 {
            font-size: 1.8rem !important;
        }
        
        /* Ensure inputs take full width without horizontal scroll */
        .stChatInputContainer {
            padding-bottom: 2rem !important;
        }
        
        /* Sidebar optimizations for mobile view */
        [data-testid="stSidebar"] {
            min-width: 100% !important;
            max-width: 100% !important;
        }
        
        /* Add some padding to main content block to avoid touching edges */
        .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            padding-top: 2rem !important;
        }
    }
    
    /* Global tweaks for better appearance */
    .stMarkdown p {
        font-size: 1.05rem;
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)

# 3. Sidebar Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    st.markdown("**Domain:** Software Engineering 💻")
    st.markdown("I can help you with:")
    st.markdown("- Code reviews & debugging\n- System architecture\n- Best practices & design patterns\n- Git & version control")
    st.markdown("---")
    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=0.2,
        step=0.1,
        help="Higher values make output more random, lower values make it more focused and deterministic."
    )
    st.markdown("---")
    if st.button("🗑️ Reset Conversation"):
        st.session_state.chat_history = []
        st.rerun()

# 4. Initialize LangChain Components
@st.cache_resource
def get_llm(temp):
    return ChatOpenAI(
        model="openrouter/auto", # Using auto to route to best available, or could specify a specific model
        openai_api_key=OPENROUTER_API_KEY,
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=temp,
        max_tokens=2048
    )

llm = get_llm(temperature)

# 5. Prompt Engineering (Mandatory criteria)
SYSTEM_PROMPT = """You are a highly skilled and professional Software Engineering AI Assistant.

Role: Expert Software Engineer and Architect.
Domain Boundaries: You ONLY answer questions related to software engineering, programming, system architecture, debugging, git/version control, and computer science concepts. 
Tone: Professional, direct, encouraging, and technically precise.

Refusal Behavior (CRITICAL): 
If the user's query is outside the domain of software engineering (e.g., medical advice, financial guidance, recipes, general history, casual chat unrelated to tech), you MUST refuse to answer. 
You must safely redirect them by saying exactly: "I am a specialized Software Engineering assistant. I cannot provide information on [Topic]. Please ask me a question related to software development, programming, or computer science."

Mandatory Output Structure:
When answering a valid domain question, you MUST format your response using EXACTLY these sections, using markdown headers:

### 1. Analysis
(Briefly analyze the problem or concept presented in the query)

### 2. Solution / Explanation
(Provide the detailed technical explanation, code snippets, or architectural design)

### 3. Best Practices
(List 1-3 professional best practices related to the topic)

### 4. Mandatory Disclaimer
*Disclaimer: The code and advice provided are for educational and structural purposes. Always review, test, and adapt code before deploying to production environments.*
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("placeholder", "{chat_history}"),
    ("user", "{input}")
])

chain = prompt | llm | StrOutputParser()

# 6. Session State Management
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 7. Main UI Content
st.title("💻 Expert Software Engineering Assistant")
st.markdown("Ask me anything about coding, architecture, or debugging.")

# Display chat history
for message in st.session_state.chat_history:
    if isinstance(message, HumanMessage):
        with st.chat_message("user", avatar="👤"):
            st.markdown(message.content)
    elif isinstance(message, AIMessage):
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(message.content)

# 8. User Input Handling
if user_query := st.chat_input("E.g., How do I resolve a merge conflict in git?"):
    # Append user message to UI immediately
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_query)
    
    # Generate and display response
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Thinking..."):
            try:
                # Execute LangChain chain
                response = chain.invoke({
                    "chat_history": st.session_state.chat_history[-5:], # Keep last 5 messages for context
                    "input": user_query
                })
                st.markdown(response)
                
                # Update history
                st.session_state.chat_history.append(HumanMessage(content=user_query))
                st.session_state.chat_history.append(AIMessage(content=response))
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
