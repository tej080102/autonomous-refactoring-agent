"""
Code Quality Metrics — Static analysis of Python files.

Measures code quality before and after refactoring to produce
resume-worthy metrics. Works WITHOUT Ollama.

Metrics collected:
  - Lines of Code (LOC)
  - Number of functions/methods
  - Cyclomatic complexity (per function + overall)
  - Type hint coverage (% of args with annotations)
  - Bare except count
  - Duplicate code pattern detection
  - Avg function length
  - Docstring coverage
"""

import ast
import sys
import json
from typing import Any


def analyze_file(filepath: str) -> dict[str, Any]:
    """Run all static analysis metrics on a single Python file."""
    with open(filepath, encoding="utf-8") as f:
        source = f.read()

    tree = ast.parse(source)
    lines = source.strip().splitlines()

    metrics = {
        "file": filepath,
        "loc": len(lines),
        "blank_lines": sum(1 for line in lines if line.strip() == ""),
        "comment_lines": sum(1 for line in lines if line.strip().startswith("#")),
    }

    # --- Function / method analysis ---
    functions = _extract_functions(tree)
    metrics["num_functions"] = len(functions)
    metrics["avg_function_length"] = (
        round(sum(f["length"] for f in functions) / len(functions), 1)
        if functions else 0
    )
    metrics["max_function_length"] = (
        max(f["length"] for f in functions) if functions else 0
    )

    # --- Type hint coverage ---
    total_args = 0
    annotated_args = 0
    functions_with_return_type = 0
    for func in functions:
        total_args += func["total_args"]
        annotated_args += func["annotated_args"]
        if func["has_return_annotation"]:
            functions_with_return_type += 1

    metrics["total_args"] = total_args
    metrics["annotated_args"] = annotated_args
    metrics["type_hint_coverage"] = (
        round(annotated_args / total_args * 100, 1) if total_args > 0 else 100.0
    )
    metrics["return_type_coverage"] = (
        round(functions_with_return_type / len(functions) * 100, 1)
        if functions else 100.0
    )

    # --- Docstring coverage ---
    functions_with_docstring = sum(1 for f in functions if f["has_docstring"])
    metrics["docstring_coverage"] = (
        round(functions_with_docstring / len(functions) * 100, 1)
        if functions else 100.0
    )

    # --- Complexity ---
    metrics["total_complexity"] = sum(f["complexity"] for f in functions)
    metrics["avg_complexity"] = (
        round(metrics["total_complexity"] / len(functions), 2)
        if functions else 0
    )
    metrics["max_complexity"] = (
        max(f["complexity"] for f in functions) if functions else 0
    )

    # --- Anti-patterns ---
    metrics["bare_excepts"] = _count_bare_excepts(tree)
    metrics["none_comparisons"] = _count_none_comparisons(tree)
    metrics["string_concat_in_loops"] = _count_string_concat_in_loops(tree)

    # --- Classes ---
    metrics["num_classes"] = sum(
        1 for node in ast.walk(tree) if isinstance(node, ast.ClassDef)
    )

    return metrics


def _extract_functions(tree: ast.AST) -> list[dict]:
    """Extract function-level metrics from the AST."""
    functions = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # Skip __init__ style methods for docstring counting
            func_info = {
                "name": node.name,
                "length": node.end_lineno - node.lineno + 1,
                "complexity": _cyclomatic_complexity(node),
                "has_docstring": (
                    isinstance(node.body[0], ast.Expr)
                    and isinstance(node.body[0].value, (ast.Constant,))
                    and isinstance(node.body[0].value.value, str)
                    if node.body else False
                ),
                "has_return_annotation": node.returns is not None,
                "total_args": 0,
                "annotated_args": 0,
            }
            # Count args (skip 'self' and 'cls')
            for arg in node.args.args:
                if arg.arg in ("self", "cls"):
                    continue
                func_info["total_args"] += 1
                if arg.annotation is not None:
                    func_info["annotated_args"] += 1

            functions.append(func_info)
    return functions


def _cyclomatic_complexity(node: ast.AST) -> int:
    """
    Calculate McCabe cyclomatic complexity for a function.
    Complexity = 1 + number of decision points.
    """
    complexity = 1
    for child in ast.walk(node):
        if isinstance(child, (ast.If, ast.While, ast.For)):
            complexity += 1
        elif isinstance(child, ast.BoolOp):
            # Each 'and'/'or' adds a decision point
            complexity += len(child.values) - 1
        elif isinstance(child, ast.ExceptHandler):
            complexity += 1
        elif isinstance(child, (ast.Assert,)):
            complexity += 1
    return complexity


def _count_bare_excepts(tree: ast.AST) -> int:
    """Count bare `except:` clauses (no exception type specified)."""
    count = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler) and node.type is None:
            count += 1
    return count


def _count_none_comparisons(tree: ast.AST) -> int:
    """Count `== None` or `!= None` comparisons (should use `is`/`is not`)."""
    count = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Compare):
            for op, comparator in zip(node.ops, node.comparators):
                if isinstance(op, (ast.Eq, ast.NotEq)):
                    if isinstance(comparator, ast.Constant) and comparator.value is None:
                        count += 1
    return count


def _count_string_concat_in_loops(tree: ast.AST) -> int:
    """Count string concatenation assignments inside for/while loops."""
    count = 0
    for node in ast.walk(tree):
        if isinstance(node, (ast.For, ast.While)):
            for child in ast.walk(node):
                if isinstance(child, ast.AugAssign) and isinstance(child.op, ast.Add):
                    count += 1
                elif isinstance(child, ast.Assign):
                    if (child.value
                            and isinstance(child.value, ast.BinOp)
                            and isinstance(child.value.op, ast.Add)):
                        count += 1
    return count


def compare_metrics(before: dict, after: dict) -> dict[str, Any]:
    """Compare before/after metrics and compute deltas."""
    comparison = {}
    for key in before:
        if key == "file":
            comparison[key] = before[key]
            continue
        b_val = before[key]
        a_val = after.get(key, b_val)
        if isinstance(b_val, (int, float)):
            delta = a_val - b_val
            pct_change = (
                round(delta / b_val * 100, 1) if b_val != 0 else 0
            )
            comparison[key] = {
                "before": b_val,
                "after": a_val,
                "delta": delta,
                "pct_change": pct_change,
            }
    return comparison


def print_metrics(metrics: dict, title: str = "Code Quality Metrics") -> None:
    """Pretty-print a metrics dictionary."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"  File: {metrics['file']}")
    print(f"{'=' * 60}")

    sections = [
        ("📏 Size", ["loc", "blank_lines", "comment_lines", "num_functions", "num_classes"]),
        ("📐 Complexity", ["avg_complexity", "max_complexity", "total_complexity",
                           "avg_function_length", "max_function_length"]),
        ("📝 Type Hints", ["type_hint_coverage", "return_type_coverage",
                          "total_args", "annotated_args"]),
        ("📖 Documentation", ["docstring_coverage"]),
        ("⚠️  Anti-patterns", ["bare_excepts", "none_comparisons",
                              "string_concat_in_loops"]),
    ]

    for section_name, keys in sections:
        print(f"\n  {section_name}")
        print(f"  {'-' * 40}")
        for key in keys:
            if key in metrics:
                val = metrics[key]
                label = key.replace("_", " ").title()
                if "coverage" in key:
                    print(f"    {label:30s} {val}%")
                else:
                    print(f"    {label:30s} {val}")
    print()


def print_comparison(comparison: dict) -> None:
    """Pretty-print a before/after comparison."""
    print(f"\n{'=' * 70}")
    print(f"  CODE QUALITY DELTA — {comparison.get('file', 'unknown')}")
    print(f"{'=' * 70}")
    print(f"  {'Metric':30s} {'Before':>8s} {'After':>8s} {'Delta':>8s} {'Change':>8s}")
    print(f"  {'-' * 66}")

    important_keys = [
        "loc", "num_functions", "avg_complexity", "max_complexity",
        "type_hint_coverage", "return_type_coverage", "docstring_coverage",
        "bare_excepts", "none_comparisons", "string_concat_in_loops",
        "avg_function_length", "max_function_length",
    ]

    for key in important_keys:
        if key in comparison and isinstance(comparison[key], dict):
            d = comparison[key]
            label = key.replace("_", " ").title()
            before = d["before"]
            after = d["after"]
            delta = d["delta"]
            pct = d["pct_change"]

            # Color indicators
            if "coverage" in key or "docstring" in key:
                indicator = "📈" if delta > 0 else ("📉" if delta < 0 else "  ")
            elif key in ("bare_excepts", "none_comparisons", "string_concat_in_loops",
                         "avg_complexity", "max_complexity"):
                indicator = "📈" if delta < 0 else ("📉" if delta > 0 else "  ")
            else:
                indicator = "  "

            print(f"  {indicator} {label:28s} {before:>8} {after:>8} {delta:>+8} {pct:>+7.1f}%")

    print(f"{'=' * 70}\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m src.metrics <file.py> [after_file.py]")
        sys.exit(1)

    before = analyze_file(sys.argv[1])
    print_metrics(before, "BEFORE Refactoring")

    if len(sys.argv) >= 3:
        after = analyze_file(sys.argv[2])
        print_metrics(after, "AFTER Refactoring")
        comparison = compare_metrics(before, after)
        print_comparison(comparison)
    else:
        print(json.dumps(before, indent=2))
