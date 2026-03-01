"""
Agent state definition for the refactoring pipeline.

This TypedDict flows through every LangGraph node, accumulating
results from planning, execution, verification, and self-repair.
"""

from typing import TypedDict


class AgentState(TypedDict):
    original_code: str        # Raw content of the input Python file
    file_path: str            # Absolute path to the file being refactored
    refactoring_plan: str     # Numbered list of refactoring actions from the planner
    refactored_code: str      # Complete refactored Python source
    test_results: str         # PyTest stdout + stderr
    test_passed: bool         # Whether pytest returned exit code 0
    retry_count: int          # Number of self-repair iterations (max 3)
    error_message: str        # Error output from failed tests
