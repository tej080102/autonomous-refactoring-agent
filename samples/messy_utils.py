"""
Intentionally messy Python module for testing the refactoring agent.

This file contains deliberate code smells:
  - Duplicated logic
  - Vague function names
  - A monolithic function that should be split
  - No type hints
  - Bare except clauses
  - Magic numbers
"""


def do_stuff(x, y):
    """Does some math stuff."""
    result = x + y
    if result > 100:
        result = result * 2
    if result < 0:
        result = 0
    return result


def do_more_stuff(x, y):
    """Does more math stuff — duplicated logic."""
    result = x + y
    if result > 100:
        result = result * 2
    if result < 0:
        result = 0
    return result * 3


def process(data):
    """Processes a list of numbers in a very messy way."""
    total = 0
    count = 0
    min_val = 999999
    max_val = -999999

    for item in data:
        try:
            val = float(item)
        except:
            continue

        total = total + val
        count = count + 1

        if val < min_val:
            min_val = val

        if val > max_val:
            max_val = val

    if count == 0:
        avg = 0
    else:
        avg = total / count

    result = {}
    result["total"] = total
    result["count"] = count
    result["average"] = avg
    result["min"] = min_val if count > 0 else None
    result["max"] = max_val if count > 0 else None

    # Determine grade based on average
    if avg >= 90:
        result["grade"] = "A"
    elif avg >= 80:
        result["grade"] = "B"
    elif avg >= 70:
        result["grade"] = "C"
    elif avg >= 60:
        result["grade"] = "D"
    else:
        result["grade"] = "F"

    return result


def handle(text):
    """Handles text processing with multiple issues."""
    if text == None:
        return ""

    result = ""
    for char in text:
        if char == " ":
            result = result + "_"
        elif char == "\t":
            result = result + "____"
        elif char == "\n":
            result = result + "\\n"
        else:
            result = result + char

    return result


def calc(a, b, c, d):
    """Calculator with too many responsibilities."""
    sum_result = a + b + c + d
    product = a * b * c * d
    average = sum_result / 4
    max_val = a
    if b > max_val:
        max_val = b
    if c > max_val:
        max_val = c
    if d > max_val:
        max_val = d
    min_val = a
    if b < min_val:
        min_val = b
    if c < min_val:
        min_val = c
    if d < min_val:
        min_val = d
    return {
        "sum": sum_result,
        "product": product,
        "average": average,
        "max": max_val,
        "min": min_val,
        "range": max_val - min_val,
    }
