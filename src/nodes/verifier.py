"""
Verifier Node — Runs PyTest against the refactored code to check correctness.

Temporarily replaces the original file with the refactored version, runs the
test suite, and restores the original regardless of outcome.
"""

import os
import shutil
import subprocess
import logging

from ..state import AgentState
from ..config import PYTEST_TIMEOUT

logger = logging.getLogger(__name__)


def verifier_node(state: AgentState) -> dict:
    """
    Write refactored code to the target file, run pytest, then restore
    the original file.

    Returns:
        dict with "test_results", "test_passed", and "error_message".
    """
    file_path = state["file_path"]
    test_dir = os.path.dirname(os.path.abspath(file_path))
    backup_path = file_path + ".bak"

    logger.info(f"🧪 Verifier: running tests in {test_dir}...")

    # --- Back up original file ---
    try:
        shutil.copy2(file_path, backup_path)
    except FileNotFoundError:
        logger.warning("Verifier: original file not found, skipping backup")

    # --- Write refactored code ---
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(state["refactored_code"])
    except OSError as exc:
        logger.error(f"Verifier: could not write refactored code — {exc}")
        return {
            "test_results": str(exc),
            "test_passed": False,
            "error_message": f"File write error: {exc}",
        }

    # --- Run pytest ---
    try:
        result = subprocess.run(
            ["python", "-m", "pytest", test_dir, "-v", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=PYTEST_TIMEOUT,
        )
        passed = result.returncode == 0
        output = result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        passed = False
        output = f"PyTest timed out after {PYTEST_TIMEOUT}s"
        logger.warning(output)
    except Exception as exc:
        passed = False
        output = f"PyTest execution error: {exc}"
        logger.error(output)

    # --- Restore original file ---
    if os.path.exists(backup_path):
        shutil.copy2(backup_path, file_path)
        os.remove(backup_path)

    if passed:
        logger.info("🧪 Verifier: all tests PASSED ✅")
    else:
        logger.info("🧪 Verifier: tests FAILED ❌")
        logger.debug(f"Test output:\n{output}")

    return {
        "test_results": output,
        "test_passed": passed,
        "error_message": output if not passed else "",
    }
