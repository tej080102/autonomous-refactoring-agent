"""
CLI entry point for the Autonomous Code Refactoring Agent.

Usage:
    python -m src.cli <file_path> [--test-dir <dir>] [--max-retries N] [--dry-run]
"""

import argparse
import logging
import sys
import os

# ANSI color codes for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"


def _setup_logging(verbose: bool = False) -> None:
    """Configure structured logging with color-coded output."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format=f"{CYAN}%(asctime)s{RESET} %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
    )


def _print_banner() -> None:
    """Print a startup banner."""
    print(f"""
{BOLD}{CYAN}╔══════════════════════════════════════════════════════════╗
║       Autonomous Code Refactoring Agent                  ║
║       Powered by DeepSeek-R1 via Ollama (local)          ║
╚══════════════════════════════════════════════════════════╝{RESET}
""")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Autonomous Code Refactoring Agent — "
        "locally refactors Python code and verifies with tests.",
    )
    parser.add_argument(
        "file_path",
        help="Path to the Python file to refactor",
    )
    parser.add_argument(
        "--test-dir",
        default=None,
        help="Directory containing tests (default: same dir as file)",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=None,
        help="Max self-repair retries (default: 3, from config)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show plan and refactored code without writing to disk",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable debug-level logging",
    )

    args = parser.parse_args()

    # --- Setup ---
    _setup_logging(args.verbose)
    _print_banner()

    # Validate input file exists
    if not os.path.isfile(args.file_path):
        print(f"{RED}❌ File not found: {args.file_path}{RESET}")
        sys.exit(1)

    if not args.file_path.endswith(".py"):
        print(f"{YELLOW}⚠️  Warning: file does not have .py extension{RESET}")

    # Override max retries if specified
    if args.max_retries is not None:
        from .config import MAX_RETRIES  # noqa: F811
        import src.config
        src.config.MAX_RETRIES = args.max_retries

    # --- Health check ---
    print(f"{CYAN}Checking Ollama connection...{RESET}")
    from .llm import check_ollama_connection
    if not check_ollama_connection():
        print(f"{RED}❌ Ollama is not ready. See errors above.{RESET}")
        sys.exit(1)
    print(f"{GREEN}✅ Ollama is ready{RESET}\n")

    # --- Run pipeline ---
    from .graph import refactor_file
    result = refactor_file(args.file_path, dry_run=args.dry_run)

    # --- Summary ---
    print(f"\n{BOLD}{'=' * 60}{RESET}")
    print(f"{BOLD} SUMMARY{RESET}")
    print(f"{'=' * 60}")
    print(f"  File:          {args.file_path}")
    print(f"  Retries used:  {result['retry_count']}")

    if result["test_passed"]:
        print(f"  Status:        {GREEN}✅ SUCCESS{RESET}")
        if args.dry_run:
            print(f"  Mode:          {YELLOW}DRY RUN (no changes written){RESET}")
    else:
        print(f"  Status:        {RED}❌ FAILED{RESET}")

    print(f"{'=' * 60}\n")

    sys.exit(0 if result["test_passed"] else 1)


if __name__ == "__main__":
    main()
