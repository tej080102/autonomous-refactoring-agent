"""
Integration tests for the LangGraph pipeline.

These tests mock the OllamaLLM to test graph routing logic
without requiring a running Ollama instance.
"""

import pytest
from unittest.mock import patch, MagicMock

from src.state import AgentState
from src.config import MAX_RETRIES


# -----------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------

def _make_initial_state(code: str = "def foo(): pass", file_path: str = "test.py") -> dict:
    """Create a minimal initial state for testing."""
    return {
        "original_code": code,
        "file_path": file_path,
        "refactoring_plan": "",
        "refactored_code": "",
        "test_results": "",
        "test_passed": False,
        "retry_count": 0,
        "error_message": "",
    }


# -----------------------------------------------------------------------
# Routing logic tests (no LLM needed)
# -----------------------------------------------------------------------

class TestShouldRetry:
    """Test the conditional routing function."""

    def test_passes_route_to_end(self):
        from src.graph import _should_retry
        state = _make_initial_state()
        state["test_passed"] = True
        assert _should_retry(state) == "end"

    def test_fails_within_retries_route_to_repair(self):
        from src.graph import _should_retry
        state = _make_initial_state()
        state["test_passed"] = False
        state["retry_count"] = 1
        assert _should_retry(state) == "repair"

    def test_fails_at_max_retries_route_to_end(self):
        from src.graph import _should_retry
        state = _make_initial_state()
        state["test_passed"] = False
        state["retry_count"] = MAX_RETRIES
        assert _should_retry(state) == "end"

    def test_fails_beyond_max_retries_route_to_end(self):
        from src.graph import _should_retry
        state = _make_initial_state()
        state["test_passed"] = False
        state["retry_count"] = MAX_RETRIES + 1
        assert _should_retry(state) == "end"


# -----------------------------------------------------------------------
# Node unit tests (mocked LLM)
# -----------------------------------------------------------------------

class TestPlannerNode:
    """Test the planner node with a mocked LLM."""

    @patch("src.nodes.planner.llm")
    def test_returns_plan(self, mock_llm):
        mock_llm.invoke.return_value = "1. Rename do_stuff to add_values"
        from src.nodes.planner import planner_node

        state = _make_initial_state()
        result = planner_node(state)

        assert "refactoring_plan" in result
        assert "Rename" in result["refactoring_plan"]
        mock_llm.invoke.assert_called_once()


class TestExecutorNode:
    """Test the executor node with a mocked LLM."""

    @patch("src.nodes.executor.llm")
    def test_valid_code_accepted(self, mock_llm):
        mock_llm.invoke.return_value = "def add_values(x, y):\n    return x + y\n"
        from src.nodes.executor import executor_node

        state = _make_initial_state()
        state["refactoring_plan"] = "1. Rename function"
        result = executor_node(state)

        assert "refactored_code" in result
        assert "add_values" in result["refactored_code"]

    @patch("src.nodes.executor.llm")
    def test_invalid_code_falls_back(self, mock_llm):
        mock_llm.invoke.return_value = "def broken(:\n    not valid"
        from src.nodes.executor import executor_node

        state = _make_initial_state()
        state["refactoring_plan"] = "1. Break everything"
        result = executor_node(state)

        # Should fall back to original code
        assert result["refactored_code"] == state["original_code"]
        assert "Syntax error" in result.get("error_message", "")

    @patch("src.nodes.executor.llm")
    def test_strips_markdown_fences(self, mock_llm):
        mock_llm.invoke.return_value = '```python\ndef clean():\n    return 1\n```'
        from src.nodes.executor import executor_node

        state = _make_initial_state()
        state["refactoring_plan"] = "1. Clean up"
        result = executor_node(state)

        assert "```" not in result["refactored_code"]
        assert "def clean" in result["refactored_code"]


class TestRepairNode:
    """Test the repair node with a mocked LLM."""

    @patch("src.nodes.repair.llm")
    def test_increments_retry(self, mock_llm):
        mock_llm.invoke.return_value = "def fixed(): pass"
        from src.nodes.repair import repair_node

        state = _make_initial_state()
        state["retry_count"] = 1
        state["error_message"] = "AssertionError"
        result = repair_node(state)

        assert result["retry_count"] == 2

    @patch("src.nodes.repair.llm")
    def test_invalid_fix_keeps_previous(self, mock_llm):
        mock_llm.invoke.return_value = "def broken(:\n"
        from src.nodes.repair import repair_node

        state = _make_initial_state()
        state["retry_count"] = 0
        state["error_message"] = "test failed"
        result = repair_node(state)

        assert result["retry_count"] == 1
        # refactored_code should not be in the result (keeping previous)
        assert "refactored_code" not in result
