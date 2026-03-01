"""
Self-Repair Node — Fixes refactored code that failed its tests.

Sends the failed code + test error output to DeepSeek-R1 and asks for
a corrected version. AST-validates the fix before accepting it.
"""

import ast
import re
import logging

from ..llm import llm
from ..state import AgentState

logger = logging.getLogger(__name__)

REPAIR_PROMPT = """The refactored code failed its tests. Fix the code to make the tests pass.
Return ONLY the corrected Python code, no explanations, no markdown fences.

FAILED CODE:
{failed_code}

TEST ERRORS:
{errors}

FIXED CODE:"""


def _strip_markdown_fences(text: str) -> str:
    """Remove common markdown code fences from LLM output."""
    text = re.sub(r"^```(?:python|py)?\s*\n?", "", text.strip())
    text = re.sub(r"\n?```\s*$", "", text.strip())
    return text.strip()


def repair_node(state: AgentState) -> dict:
    """
    Attempt to fix the refactored code based on test errors.

    Always increments retry_count. If the LLM output fails AST validation,
    the previous refactored_code is kept (so the verifier can re-run and
    report the same error, eventually hitting max retries).

    Returns:
        dict with "refactored_code" and "retry_count".
    """
    attempt = state["retry_count"] + 1
    logger.info(f"🔧 Repair: attempt {attempt} — reading errors and patching code...")

    raw_output = llm.invoke(
        REPAIR_PROMPT.format(
            failed_code=state["refactored_code"],
            errors=state["error_message"],
        )
    )

    fixed = _strip_markdown_fences(raw_output)

    try:
        ast.parse(fixed)
        logger.info(f"🔧 Repair: attempt {attempt} — fixed code passes AST validation ✅")
        return {
            "refactored_code": fixed,
            "retry_count": attempt,
        }
    except SyntaxError as exc:
        logger.warning(
            f"🔧 Repair: attempt {attempt} — AST validation FAILED ({exc}), "
            "keeping previous code"
        )
        return {"retry_count": attempt}
