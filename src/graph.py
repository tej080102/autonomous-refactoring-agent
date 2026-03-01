"""
LangGraph state machine for the Autonomous Code Refactoring Agent.

Wires the Planner → Executor → Verifier → (Self-Repair loop) graph
with conditional edges for retry logic.
"""

import os
import shutil
import logging

from langgraph.graph import StateGraph, END

from .state import AgentState
from .config import MAX_RETRIES
from .nodes.planner import planner_node
from .nodes.executor import executor_node
from .nodes.verifier import verifier_node
from .nodes.repair import repair_node

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Conditional routing after verification
# ---------------------------------------------------------------------------

def _should_retry(state: AgentState) -> str:
    """
    Route after the verifier node:
      - "end"    → tests passed OR max retries reached
      - "repair" → tests failed and retries remaining
    """
    if state["test_passed"]:
        return "end"
    if state["retry_count"] >= MAX_RETRIES:
        logger.warning(
            f"⚠️  Max retries ({MAX_RETRIES}) reached — giving up on self-repair"
        )
        return "end"
    return "repair"


# ---------------------------------------------------------------------------
# Build and compile the graph
# ---------------------------------------------------------------------------

graph = StateGraph(AgentState)

graph.add_node("planner", planner_node)
graph.add_node("executor", executor_node)
graph.add_node("verifier", verifier_node)
graph.add_node("repair", repair_node)

graph.set_entry_point("planner")
graph.add_edge("planner", "executor")
graph.add_edge("executor", "verifier")
graph.add_conditional_edges(
    "verifier",
    _should_retry,
    {"end": END, "repair": "repair"},
)
graph.add_edge("repair", "verifier")

app = graph.compile()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def refactor_file(file_path: str, dry_run: bool = False) -> dict:
    """
    Run the full refactoring pipeline on a single Python file.

    Args:
        file_path: Path to the Python file to refactor.
        dry_run:   If True, print the plan and refactored code but do NOT
                   write changes to disk.

    Returns:
        The final AgentState dict with all results.
    """
    abs_path = os.path.abspath(file_path)
    logger.info(f"🚀 Starting refactoring pipeline for: {abs_path}")

    with open(abs_path, encoding="utf-8") as f:
        code = f.read()

    result = app.invoke({
        "original_code": code,
        "file_path": abs_path,
        "refactoring_plan": "",
        "refactored_code": "",
        "test_results": "",
        "test_passed": False,
        "retry_count": 0,
        "error_message": "",
    })

    # --- Output results ---
    if result["test_passed"]:
        if dry_run:
            print("\n" + "=" * 60)
            print("DRY RUN — refactored code NOT written to disk")
            print("=" * 60)
            print("\n📋 REFACTORING PLAN:")
            print(result["refactoring_plan"])
            print("\n📝 REFACTORED CODE:")
            print(result["refactored_code"])
        else:
            # Create backup and write refactored code
            backup_path = abs_path + ".bak"
            shutil.copy2(abs_path, backup_path)
            with open(abs_path, "w", encoding="utf-8") as f:
                f.write(result["refactored_code"])
            print(f"\n✅ Refactoring successful!")
            print(f"   Backup saved to: {backup_path}")
            print(f"   Refactored file: {abs_path}")
    else:
        print(f"\n❌ Refactoring failed after {result['retry_count']} retries")
        print(f"   Original file preserved (unchanged)")
        if result["error_message"]:
            print(f"\n   Last error:\n{result['error_message'][:500]}")

    return result
