"""
Sample 5: Math/statistics with code smells.
Issues: repeated patterns, no type hints, manual reimplementation of builtins,
        magic numbers, poor variable naming.
"""


def m(numbers):
    """Mean."""
    t = 0
    c = 0
    for n in numbers:
        t = t + n
        c = c + 1
    if c == 0:
        return 0
    return t / c


def md(numbers):
    """Median."""
    s = list(numbers)
    for i in range(len(s)):
        for j in range(i + 1, len(s)):
            if s[j] < s[i]:
                temp = s[i]
                s[i] = s[j]
                s[j] = temp
    n = len(s)
    if n == 0:
        return 0
    if n % 2 == 1:
        return s[n // 2]
    else:
        return (s[n // 2 - 1] + s[n // 2]) / 2


def sd(numbers):
    """Standard deviation."""
    mean = m(numbers)
    t = 0
    c = 0
    for n in numbers:
        t = t + (n - mean) ** 2
        c = c + 1
    if c == 0:
        return 0
    return (t / c) ** 0.5


def pct(numbers, p):
    """Percentile."""
    s = list(numbers)
    for i in range(len(s)):
        for j in range(i + 1, len(s)):
            if s[j] < s[i]:
                temp = s[i]
                s[i] = s[j]
                s[j] = temp
    if len(s) == 0:
        return 0
    k = (len(s) - 1) * (p / 100.0)
    f = int(k)
    c = f + 1 if f + 1 < len(s) else f
    return s[f] + (s[c] - s[f]) * (k - f)


def describe(numbers):
    """Full statistical summary."""
    return {
        "mean": m(numbers),
        "median": md(numbers),
        "std": sd(numbers),
        "min": min(numbers) if numbers else 0,
        "max": max(numbers) if numbers else 0,
        "p25": pct(numbers, 25),
        "p75": pct(numbers, 75),
        "count": len(numbers),
    }
