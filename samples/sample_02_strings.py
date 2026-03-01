"""
Sample 2: String manipulation with poor practices.
Issues: string concatenation in loops, no type hints, magic numbers,
duplicated validation, poor naming.
"""


def chk(s):
    if s == None:
        return False
    if len(s) == 0:
        return False
    if len(s) > 255:
        return False
    return True


def chk2(s):
    if s == None:
        return False
    if len(s) == 0:
        return False
    if len(s) > 255:
        return False
    for c in s:
        if not c.isalnum() and c != "_":
            return False
    return True


def fmt(items):
    result = ""
    for i in range(len(items)):
        if i == len(items) - 1:
            result = result + str(items[i])
        else:
            result = result + str(items[i]) + ", "
    return result


def fmt_table(headers, rows):
    output = ""
    # Header
    for i in range(len(headers)):
        output = output + headers[i]
        if i < len(headers) - 1:
            output = output + " | "
    output = output + "\n"
    # Separator
    for i in range(len(headers)):
        output = output + "---"
        if i < len(headers) - 1:
            output = output + " | "
    output = output + "\n"
    # Rows
    for row in rows:
        for i in range(len(row)):
            output = output + str(row[i])
            if i < len(row) - 1:
                output = output + " | "
        output = output + "\n"
    return output


def count_words(text):
    if text == None:
        return {}
    words = text.split()
    counts = {}
    for w in words:
        w = w.lower()
        w = w.strip(".,!?;:'\"")
        if w in counts:
            counts[w] = counts[w] + 1
        else:
            counts[w] = 1
    return counts
