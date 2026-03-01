"""
Planner Node — Analyzes input code and produces a concrete refactoring plan.

The planner asks DeepSeek-R1 to identify code smells and output a numbered
list of specific refactoring actions (DRY, naming, function size, type hints,
error handling).
"""

import logging
from ..llm import llm
from ..state import AgentState

logger = logging.getLogger(__name__)

PLANNER_PROMPT = """You are a code refactoring expert. Analyze the following Python code \
and create a concrete refactoring plan. Focus on:
- Removing code duplication (DRY principle)
- Improving function naming and clarity
- Breaking large functions into smaller ones
- Adding type hints where missing
- Improving error handling

CODE:
{code}

Output a numbered list of specific refactoring actions to take. Be concrete \
and reference the exact function/variable names you want to change."""


def planner_node(state: AgentState) -> dict:
    """
    Analyze the original code and produce a refactoring plan.

    Returns:
        dict with "refactoring_plan" key.
    """
    logger.info("📋 Planner: analyzing code and generating refactoring plan...")

    plan = llm.invoke(PLANNER_PROMPT.format(code=state["original_code"]))

    logger.info("📋 Planner: plan generated successfully")
    logger.debug(f"Plan:\n{plan}")

    return {"refactoring_plan": plan}
