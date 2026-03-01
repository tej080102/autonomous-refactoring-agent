"""
Benchmark Runner — Comprehensive metrics for the Autonomous Code Refactoring Agent.

Runs the full pipeline on all 10 sample files and produces a detailed
benchmark report with resume-worthy metrics.

Metrics collected per file:
  ┌─────────────────────────────────┐
  │  Pipeline Metrics               │
  │  • Success rate (pass/fail)     │
  │  • Retries used                 │
  │  • AST validation passes        │
  │  • Per-stage latency            │
  │  • Total pipeline time          │
  ├─────────────────────────────────┤
  │  Code Quality Delta             │
  │  • LOC change                   │
  │  • Complexity reduction         │
  │  • Type hint coverage gain      │
  │  • Anti-pattern elimination     │
  │  • Function decomposition       │
  │  • Docstring coverage gain      │
  └─────────────────────────────────┘

Usage:
    python benchmark.py                   # Full benchmark (needs Ollama)
    python benchmark.py --metrics-only    # Code quality metrics only (no Ollama)
    python benchmark.py --report          # Generate JSON report
"""

import os
import sys
import json
import time
import shutil
import subprocess
import glob
import argparse
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.metrics import analyze_file, compare_metrics, print_metrics, print_comparison


# ── ANSI Colors ──────────────────────────────────────────────────────────────
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

# ── Sample file registry ────────────────────────────────────────────────────
SAMPLES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "samples")

SAMPLE_FILES = [
    ("messy_utils.py", "test_messy_utils.py", "General utilities"),
    ("sample_02_strings.py", "test_sample_02_strings.py", "String manipulation"),
    ("sample_03_data.py", "test_sample_03_data.py", "Data processing"),
    ("sample_04_csv.py", "test_sample_04_csv.py", "CSV operations"),
    ("sample_05_math.py", "test_sample_05_math.py", "Math/statistics"),
    ("sample_06_cart.py", "test_sample_06_cart.py", "Shopping cart OOP"),
    ("sample_07_auth.py", "test_sample_07_auth.py", "Auth/password"),
    ("sample_08_tasks.py", "test_sample_08_tasks.py", "Task manager"),
    ("sample_09_matrix.py", "test_sample_09_matrix.py", "Matrix operations"),
    ("sample_10_inventory.py", "test_sample_10_inventory.py", "Inventory system"),
]


def run_metrics_only() -> dict:
    """
    Analyze all sample files for code quality metrics WITHOUT running the LLM.
    This is useful for establishing the baseline.
    """
    print(f"\n{BOLD}{CYAN}╔══════════════════════════════════════════════════════════╗")
    print(f"║       Code Quality Baseline — All 10 Samples            ║")
    print(f"╚══════════════════════════════════════════════════════════╝{RESET}\n")

    all_metrics = []
    totals = {
        "total_loc": 0,
        "total_functions": 0,
        "total_complexity": 0,
        "total_bare_excepts": 0,
        "total_none_comparisons": 0,
        "total_string_concat_in_loops": 0,
        "total_args": 0,
        "annotated_args": 0,
        "files_analyzed": 0,
    }

    for source_file, _, description in SAMPLE_FILES:
        path = os.path.join(SAMPLES_DIR, source_file)
        if not os.path.exists(path):
            print(f"  {YELLOW}⚠ Skipping {source_file} (not found){RESET}")
            continue

        metrics = analyze_file(path)
        all_metrics.append(metrics)
        totals["files_analyzed"] += 1
        totals["total_loc"] += metrics["loc"]
        totals["total_functions"] += metrics["num_functions"]
        totals["total_complexity"] += metrics["total_complexity"]
        totals["total_bare_excepts"] += metrics["bare_excepts"]
        totals["total_none_comparisons"] += metrics["none_comparisons"]
        totals["total_string_concat_in_loops"] += metrics["string_concat_in_loops"]
        totals["total_args"] += metrics["total_args"]
        totals["annotated_args"] += metrics["annotated_args"]

        # Print compact summary per file
        print(f"  {BOLD}{source_file:30s}{RESET} {DIM}({description}){RESET}")
        print(f"    LOC: {metrics['loc']:>4d}  |  "
              f"Functions: {metrics['num_functions']:>3d}  |  "
              f"Avg Complexity: {metrics['avg_complexity']:>5.1f}  |  "
              f"Type Hints: {metrics['type_hint_coverage']:>5.1f}%  |  "
              f"Bare Excepts: {metrics['bare_excepts']}")

    # --- Aggregate Summary ---
    print(f"\n{BOLD}{'=' * 70}")
    print(f"  AGGREGATE BASELINE (across {totals['files_analyzed']} files)")
    print(f"{'=' * 70}{RESET}")
    print(f"  Total Lines of Code:              {totals['total_loc']}")
    print(f"  Total Functions:                  {totals['total_functions']}")
    print(f"  Total Cyclomatic Complexity:       {totals['total_complexity']}")
    avg_complexity = (
        round(totals["total_complexity"] / totals["total_functions"], 2)
        if totals["total_functions"] else 0
    )
    print(f"  Avg Complexity per Function:       {avg_complexity}")
    type_coverage = (
        round(totals["annotated_args"] / totals["total_args"] * 100, 1)
        if totals["total_args"] else 100
    )
    print(f"  Type Hint Coverage:               {type_coverage}%")
    print(f"  Bare Except Clauses:              {totals['total_bare_excepts']}")
    print(f"  None == Comparisons:              {totals['total_none_comparisons']}")
    print(f"  String Concat in Loops:           {totals['total_string_concat_in_loops']}")
    print(f"{'=' * 70}\n")

    return {"files": all_metrics, "totals": totals}


def run_full_benchmark(dry_run: bool = False) -> dict:
    """
    Run the full refactoring pipeline on all 10 samples and measure everything.
    Requires Ollama with deepseek-r1:7b.
    """
    from src.llm import check_ollama_connection
    from src.graph import refactor_file

    print(f"\n{BOLD}{CYAN}╔══════════════════════════════════════════════════════════╗")
    print(f"║       Full Benchmark — 10 Samples                       ║")
    print(f"╚══════════════════════════════════════════════════════════╝{RESET}\n")

    if not check_ollama_connection():
        print(f"{RED}❌ Ollama is not ready. Run with --metrics-only for static analysis.{RESET}")
        return {}

    results = []
    total_success = 0
    total_retries = 0
    total_time = 0

    for i, (source_file, test_file, description) in enumerate(SAMPLE_FILES, 1):
        source_path = os.path.join(SAMPLES_DIR, source_file)
        if not os.path.exists(source_path):
            print(f"  {YELLOW}⚠ Skipping {source_file}{RESET}")
            continue

        print(f"\n{BOLD}[{i}/10] {source_file}{RESET} {DIM}({description}){RESET}")
        print(f"  {'─' * 50}")

        # --- Before metrics ---
        before_metrics = analyze_file(source_path)

        # --- Run pipeline with timing ---
        start_time = time.time()

        # Create a working copy so we don't mess up the originals
        work_dir = os.path.join(SAMPLES_DIR, ".benchmark_work")
        os.makedirs(work_dir, exist_ok=True)
        work_source = os.path.join(work_dir, source_file)
        work_test = os.path.join(work_dir, test_file)
        shutil.copy2(source_path, work_source)
        shutil.copy2(os.path.join(SAMPLES_DIR, test_file), work_test)

        try:
            result = refactor_file(work_source, dry_run=dry_run)
            elapsed = time.time() - start_time
            success = result.get("test_passed", False)
            retries = result.get("retry_count", 0)

            # --- After metrics (only if success) ---
            after_metrics = None
            comparison = None
            if success and os.path.exists(work_source):
                after_metrics = analyze_file(work_source)
                comparison = compare_metrics(before_metrics, after_metrics)

            file_result = {
                "file": source_file,
                "description": description,
                "success": success,
                "retries": retries,
                "elapsed_seconds": round(elapsed, 2),
                "before_metrics": before_metrics,
                "after_metrics": after_metrics,
                "comparison": comparison,
            }
            results.append(file_result)

            if success:
                total_success += 1
                print(f"  {GREEN}✅ PASS{RESET} — {retries} retries — {elapsed:.1f}s")
                if comparison:
                    _print_compact_comparison(comparison)
            else:
                print(f"  {RED}❌ FAIL{RESET} — {retries} retries — {elapsed:.1f}s")

            total_retries += retries
            total_time += elapsed

        except Exception as exc:
            elapsed = time.time() - start_time
            print(f"  {RED}❌ ERROR: {exc}{RESET}")
            results.append({
                "file": source_file,
                "success": False,
                "retries": 0,
                "elapsed_seconds": round(elapsed, 2),
                "error": str(exc),
            })

        finally:
            # Clean up working directory
            if os.path.exists(work_dir):
                shutil.rmtree(work_dir, ignore_errors=True)

    # --- Final Report ---
    _print_final_report(results, total_success, total_retries, total_time)

    return {
        "results": results,
        "summary": {
            "total_files": len(results),
            "successes": total_success,
            "success_rate": round(total_success / len(results) * 100, 1) if results else 0,
            "total_retries": total_retries,
            "avg_retries": round(total_retries / len(results), 2) if results else 0,
            "total_time": round(total_time, 2),
            "avg_time_per_file": round(total_time / len(results), 2) if results else 0,
            "timestamp": datetime.now().isoformat(),
        }
    }


def _print_compact_comparison(comparison: dict) -> None:
    """Print a one-line summary of key improvements."""
    improvements = []
    for key, label in [
        ("type_hint_coverage", "Type Hints"),
        ("bare_excepts", "Bare Excepts"),
        ("avg_complexity", "Complexity"),
        ("loc", "LOC"),
    ]:
        if key in comparison and isinstance(comparison[key], dict):
            d = comparison[key]
            if d["delta"] != 0:
                if key in ("bare_excepts", "avg_complexity", "loc"):
                    arrow = "↓" if d["delta"] < 0 else "↑"
                else:
                    arrow = "↑" if d["delta"] > 0 else "↓"
                improvements.append(f"{label} {arrow}{abs(d['delta'])}")

    if improvements:
        print(f"    {DIM}Improvements: {', '.join(improvements)}{RESET}")


def _print_final_report(results, total_success, total_retries, total_time):
    """Print the final benchmark summary."""
    n = len(results)
    success_rate = round(total_success / n * 100, 1) if n else 0

    print(f"\n\n{BOLD}{CYAN}{'═' * 70}")
    print(f"  BENCHMARK RESULTS — {n} FILES")
    print(f"{'═' * 70}{RESET}")

    # Success/fail per file
    for r in results:
        status = f"{GREEN}✅ PASS{RESET}" if r["success"] else f"{RED}❌ FAIL{RESET}"
        retries = r.get("retries", 0)
        elapsed = r.get("elapsed_seconds", 0)
        print(f"  {status}  {r['file']:30s}  retries: {retries}  time: {elapsed:.1f}s")

    print(f"\n{BOLD}  ┌────────────────────────────────────────────────────┐")
    print(f"  │  RESUME METRICS                                      │")
    print(f"  ├────────────────────────────────────────────────────┤")
    print(f"  │  Success Rate:          {success_rate:>6.1f}% ({total_success}/{n} files)   │")
    print(f"  │  Total Retries:         {total_retries:>6d}                       │")
    print(f"  │  Avg Retries/File:      {total_retries/n if n else 0:>6.2f}                       │")
    print(f"  │  Total Pipeline Time:   {total_time:>6.1f}s                      │")
    print(f"  │  Avg Time/File:         {total_time/n if n else 0:>6.1f}s                      │")
    print(f"  └────────────────────────────────────────────────────┘{RESET}")

    # Aggregate code quality improvements
    successful = [r for r in results if r["success"] and r.get("comparison")]
    if successful:
        _print_aggregate_quality(successful)

    print()


def _print_aggregate_quality(successful_results):
    """Aggregate and print code quality improvements across all successful files."""
    totals = {}
    keys = [
        "loc", "avg_complexity", "max_complexity",
        "type_hint_coverage", "return_type_coverage", "docstring_coverage",
        "bare_excepts", "none_comparisons", "string_concat_in_loops",
        "avg_function_length", "num_functions",
    ]

    for key in keys:
        before_sum = 0
        after_sum = 0
        count = 0
        for r in successful_results:
            comp = r["comparison"]
            if key in comp and isinstance(comp[key], dict):
                before_sum += comp[key]["before"]
                after_sum += comp[key]["after"]
                count += 1
        if count > 0:
            totals[key] = {
                "avg_before": round(before_sum / count, 2),
                "avg_after": round(after_sum / count, 2),
                "avg_delta": round((after_sum - before_sum) / count, 2),
            }

    n = len(successful_results)
    print(f"\n{BOLD}  ┌────────────────────────────────────────────────────┐")
    print(f"  │  CODE QUALITY IMPROVEMENTS (avg across {n} files)     │")
    print(f"  ├────────────────────────────────────────────────────┤{RESET}")

    for key, label in [
        ("loc", "Lines of Code"),
        ("avg_complexity", "Avg Cyclomatic Complexity"),
        ("type_hint_coverage", "Type Hint Coverage (%)"),
        ("docstring_coverage", "Docstring Coverage (%)"),
        ("bare_excepts", "Bare Except Clauses"),
        ("none_comparisons", "None == Comparisons"),
        ("string_concat_in_loops", "String Concat in Loops"),
        ("num_functions", "Number of Functions"),
        ("avg_function_length", "Avg Function Length"),
    ]:
        if key in totals:
            t = totals[key]
            delta_str = f"{t['avg_delta']:+.1f}"
            print(f"  │  {label:32s} {t['avg_before']:>7.1f} → {t['avg_after']:>7.1f} ({delta_str:>6s}) │")

    print(f"  └────────────────────────────────────────────────────┘")


def main():
    parser = argparse.ArgumentParser(description="Benchmark the refactoring agent")
    parser.add_argument(
        "--metrics-only",
        action="store_true",
        help="Only run static code quality analysis (no Ollama needed)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run pipeline in dry-run mode (no file writes)",
    )
    parser.add_argument(
        "--report",
        type=str,
        default=None,
        help="Save detailed report as JSON to the given path",
    )
    args = parser.parse_args()

    if args.metrics_only:
        result = run_metrics_only()
    else:
        result = run_full_benchmark(dry_run=args.dry_run)

    if args.report and result:
        # Make results JSON-serializable
        with open(args.report, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, default=str)
        print(f"\n📄 Report saved to: {args.report}")


if __name__ == "__main__":
    main()
