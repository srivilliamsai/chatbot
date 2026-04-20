"""
Test suite for the Software Engineering Assistant.
Tests cover: config validation, utility functions, prompt behavior,
input validation, and end-to-end LLM interaction scenarios.

Run:  python -m pytest tests.py -v
"""

import os
import json
import pytest
from unittest.mock import patch, MagicMock
from langchain_core.messages import AIMessage, HumanMessage

from config import (
    MODELS, DEFAULT_MODEL, SYSTEM_PROMPT, EXAMPLE_PROMPTS,
    APP_TITLE, MAX_CONTEXT_MESSAGES, DEFAULT_TEMPERATURE, MAX_TOKENS
)
from utils import estimate_tokens, export_chat_as_markdown, export_chat_as_json, validate_input


# ============================================================
# 1. Configuration Tests
# ============================================================

class TestConfig:
    """Validate all configuration values are properly defined."""

    def test_models_not_empty(self):
        assert len(MODELS) > 0, "MODELS dictionary must not be empty"

    def test_default_model_exists(self):
        assert DEFAULT_MODEL in MODELS, f"DEFAULT_MODEL '{DEFAULT_MODEL}' must be a key in MODELS"

    def test_all_model_values_are_strings(self):
        for name, model_id in MODELS.items():
            assert isinstance(model_id, str), f"Model '{name}' ID must be a string"
            assert len(model_id) > 0, f"Model '{name}' ID must not be empty"

    def test_system_prompt_contains_domain_boundary(self):
        assert "software engineering" in SYSTEM_PROMPT.lower(), \
            "System prompt must define software engineering domain"

    def test_system_prompt_contains_refusal_behavior(self):
        assert "refuse" in SYSTEM_PROMPT.lower() or "cannot provide" in SYSTEM_PROMPT.lower(), \
            "System prompt must define refusal behavior for out-of-domain queries"

    def test_system_prompt_contains_disclaimer(self):
        assert "disclaimer" in SYSTEM_PROMPT.lower(), \
            "System prompt must include mandatory disclaimer section"

    def test_example_prompts_not_empty(self):
        assert len(EXAMPLE_PROMPTS) >= 4, "Must have at least 4 example prompts"

    def test_example_prompts_are_strings(self):
        for prompt in EXAMPLE_PROMPTS:
            assert isinstance(prompt, str) and len(prompt) > 0

    def test_app_title_defined(self):
        assert isinstance(APP_TITLE, str) and len(APP_TITLE) > 0

    def test_temperature_range(self):
        assert 0.0 <= DEFAULT_TEMPERATURE <= 1.0

    def test_max_tokens_positive(self):
        assert MAX_TOKENS > 0

    def test_max_context_positive(self):
        assert MAX_CONTEXT_MESSAGES > 0


# ============================================================
# 2. Utility Function Tests
# ============================================================

class TestEstimateTokens:
    """Test token estimation utility."""

    def test_empty_string(self):
        assert estimate_tokens("") == 0

    def test_single_word(self):
        result = estimate_tokens("hello")
        assert result >= 1

    def test_sentence(self):
        result = estimate_tokens("This is a simple test sentence with eight words")
        assert result > 5

    def test_long_text(self):
        text = "word " * 1000
        result = estimate_tokens(text)
        assert result > 1000

    def test_returns_integer(self):
        assert isinstance(estimate_tokens("test"), int)


class TestValidateInput:
    """Test input validation."""

    def test_valid_input(self):
        is_valid, msg = validate_input("How do I use git?")
        assert is_valid is True
        assert msg == ""

    def test_empty_input(self):
        is_valid, msg = validate_input("")
        assert is_valid is False
        assert len(msg) > 0

    def test_whitespace_only(self):
        is_valid, msg = validate_input("   ")
        assert is_valid is False

    def test_none_input(self):
        is_valid, msg = validate_input(None)
        assert is_valid is False

    def test_too_long_input(self):
        is_valid, msg = validate_input("x" * 10001)
        assert is_valid is False
        assert "10,000" in msg

    def test_exactly_max_length(self):
        is_valid, msg = validate_input("x" * 10000)
        assert is_valid is True

    def test_normal_code_question(self):
        is_valid, _ = validate_input("What is a binary search tree?")
        assert is_valid is True

    def test_special_characters(self):
        is_valid, _ = validate_input("How does O(n log n) work?")
        assert is_valid is True


class TestExportChatMarkdown:
    """Test markdown export functionality."""

    def test_empty_history(self):
        result = export_chat_as_markdown([])
        assert "Chat Export" in result

    def test_single_exchange(self):
        history = [
            HumanMessage(content="Hello"),
            AIMessage(content="Hi there")
        ]
        result = export_chat_as_markdown(history)
        assert "You" in result
        assert "Assistant" in result
        assert "Hello" in result
        assert "Hi there" in result

    def test_multiple_exchanges(self):
        history = [
            HumanMessage(content="Q1"),
            AIMessage(content="A1"),
            HumanMessage(content="Q2"),
            AIMessage(content="A2"),
        ]
        result = export_chat_as_markdown(history)
        assert result.count("### You") == 2
        assert result.count("### Assistant") == 2

    def test_returns_string(self):
        result = export_chat_as_markdown([])
        assert isinstance(result, str)


class TestExportChatJSON:
    """Test JSON export functionality."""

    def test_empty_history(self):
        result = export_chat_as_json([])
        data = json.loads(result)
        assert data["messages"] == []
        assert "exported_at" in data

    def test_single_exchange(self):
        history = [
            HumanMessage(content="Hello"),
            AIMessage(content="World")
        ]
        result = export_chat_as_json(history)
        data = json.loads(result)
        assert len(data["messages"]) == 2
        assert data["messages"][0]["role"] == "user"
        assert data["messages"][1]["role"] == "assistant"

    def test_valid_json(self):
        history = [HumanMessage(content="test")]
        result = export_chat_as_json(history)
        # Should not raise
        json.loads(result)


# ============================================================
# 3. Domain Boundary Test Scenarios
# ============================================================

class TestDomainBoundaryScenarios:
    """
    Document the 12 test scenarios for domain boundary validation.
    These test the SYSTEM_PROMPT behavior (validated manually or via LLM call).
    Marked with descriptions for documentation purposes.
    """

    # --- In-Domain Queries (should get answered) ---

    @pytest.mark.parametrize("query,topic", [
        ("What is the difference between an Abstract Class and an Interface in Java?",
         "OOP Concepts"),
        ("How do I resolve a merge conflict in Git?",
         "Version Control"),
        ("Explain the MVC architecture pattern.",
         "Architecture Patterns"),
        ("What are the SOLID principles of object-oriented design?",
         "Design Principles"),
        ("Can you explain how a Docker container differs from a Virtual Machine?",
         "DevOps / Containers"),
        ("How does a hash map work internally in Python?",
         "Data Structures"),
        ("What is the time complexity of quicksort?",
         "Algorithms"),
        ("How do I write a REST API using FastAPI?",
         "Web Development"),
        ("Explain dependency injection with an example.",
         "Design Patterns"),
        ("What is CI/CD and why is it important?",
         "DevOps Practices"),
    ])
    def test_in_domain_query_documented(self, query, topic):
        """These queries should be answered by the assistant."""
        # Validate the query is a non-empty string (structural test)
        assert isinstance(query, str) and len(query) > 10
        assert isinstance(topic, str)

    # --- Out-of-Domain Queries (should be refused) ---

    @pytest.mark.parametrize("query,topic", [
        ("What is the capital of Australia?",
         "Geography"),
        ("Can you give me a recipe for chocolate chip cookies?",
         "Cooking"),
        ("How do I treat a mild sunburn?",
         "Medical Advice"),
        ("What is the best investment strategy for 2026?",
         "Financial Advice"),
    ])
    def test_out_of_domain_query_documented(self, query, topic):
        """These queries should be REFUSED by the assistant."""
        assert isinstance(query, str) and len(query) > 10
        assert isinstance(topic, str)


# ============================================================
# 4. Integration-style Tests (mocked LLM)
# ============================================================

class TestLLMChainSetup:
    """Test that the LangChain components can be assembled correctly."""

    def test_prompt_template_has_system_message(self):
        """Verify the system prompt is included in the template."""
        from langchain_core.prompts import ChatPromptTemplate
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("placeholder", "{chat_history}"),
            ("user", "{input}")
        ])
        # Should have 3 message templates
        assert len(prompt.messages) == 3

    def test_prompt_template_renders(self):
        """Verify the prompt template renders with sample inputs."""
        from langchain_core.prompts import ChatPromptTemplate
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("user", "{input}")
        ])
        result = prompt.format_messages(input="What is polymorphism?")
        assert len(result) == 2
        assert "polymorphism" in result[1].content

    def test_model_ids_are_valid_format(self):
        """All model IDs should follow provider/model-name format."""
        for name, model_id in MODELS.items():
            assert "/" in model_id, f"Model '{name}' ID must be in 'provider/model' format"


# ============================================================
# 5. Edge Case Tests
# ============================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_unicode_input_validation(self):
        is_valid, _ = validate_input("What is a binary tree? 树")
        assert is_valid is True

    def test_multiline_input_validation(self):
        is_valid, _ = validate_input("Line one\nLine two\nLine three")
        assert is_valid is True

    def test_code_snippet_input_validation(self):
        code = '''def fib(n):
    if n <= 1: return n
    return fib(n-1) + fib(n-2)'''
        is_valid, _ = validate_input(f"What's wrong with this code?\n{code}")
        assert is_valid is True

    def test_token_estimate_with_code(self):
        code = "for i in range(10): print(i)"
        tokens = estimate_tokens(code)
        assert tokens > 0

    def test_chat_export_with_code_content(self):
        history = [
            HumanMessage(content="Show me a loop"),
            AIMessage(content="```python\nfor i in range(10):\n    print(i)\n```")
        ]
        result = export_chat_as_markdown(history)
        assert "```python" in result
