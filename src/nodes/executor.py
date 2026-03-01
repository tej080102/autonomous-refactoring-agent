"""
Executor Node — Applies the refactoring plan to the original code.

The executor sends the original code + plan to DeepSeek-R1, asks for the
complete refactored source, and validates the output with ast.parse() before
accepting it.
"""

import ast
import re
import logging

from ..llm import llm
from ..state import AgentState

logger = logging.getLogger(__name__)

EXECUTOR_PROMPT = """You are a Python expert. Apply the following refactoring plan to the code.
Return ONLY the complete refactored Python code, no explanations, no markdown fences.

ORIGINAL CODE:
{original_code}

REFACTORING PLAN:
{plan}

REFACTORED CODE:"""


def _strip_markdown_fences(text: str) -> str:
    """
    Remove common markdown code fences that LLMs sometimes wrap around output.
    Handles ```python ... ``` and ``` ... ``` patterns.
    """
    # Remove opening fence (with optional language tag)
    text = re.sub(r"^```(?:python|py)?\s*\n?", "", text.strip())
    # Remove closing fence
    text = re.sub(r"\n?```\s*$", "", text.strip())
    return text.strip()


def executor_node(state: AgentState) -> dict:
    """
    Apply the refactoring plan and return validated Python code.

    If the generated code has a SyntaxError, the original code is preserved
    and the error is recorded in error_message.

    Returns:
        dict with "refactored_code" (and possibly "error_message").
    """
    logger.info("⚙️  Executor: applying refactoring plan to code...")

    raw_output = llm.invoke(
        EXECUTOR_PROMPT.format(
            original_code=state["original_code"],
            plan=state["refactoring_plan"],
        )
    )

    refactored = _strip_markdown_fences(raw_output)

    # Validate that the output is parseable Python
    try:
        ast.parse(refactored)
        logger.info("⚙️  Executor: refactored code passes AST validation ✅")
        return {"refactored_code": refactored}
    except SyntaxError as exc:
        logger.warning(f"⚙️  Executor: AST validation FAILED — {exc}")
        return {
            "refactored_code": state["original_code"],
            "error_message": f"Syntax error in generated code: {exc}",
        }
