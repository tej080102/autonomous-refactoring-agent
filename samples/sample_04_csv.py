"""
Sample 4: File-like operations with poor patterns.
Issues: duplicated parsing, manual CSV building, no type hints, magic strings.
"""


def parse_csv_line(line):
    result = []
    current = ""
    in_quotes = False
    for char in line:
        if char == '"':
            in_quotes = not in_quotes
        elif char == ',' and not in_quotes:
            result.append(current.strip())
            current = ""
        else:
            current = current + char
    result.append(current.strip())
    return result


def parse_csv(text):
    lines = text.strip().split("\n")
    if len(lines) == 0:
        return []
    headers = parse_csv_line(lines[0])
    rows = []
    for i in range(1, len(lines)):
        values = parse_csv_line(lines[i])
        row = {}
        for j in range(len(headers)):
            if j < len(values):
                row[headers[j]] = values[j]
            else:
                row[headers[j]] = ""
        rows.append(row)
    return rows


def to_csv(headers, rows):
    output = ""
    for i in range(len(headers)):
        output = output + headers[i]
        if i < len(headers) - 1:
            output = output + ","
    output = output + "\n"
    for row in rows:
        for i in range(len(headers)):
            val = str(row.get(headers[i], ""))
            if "," in val:
                val = '"' + val + '"'
            output = output + val
            if i < len(headers) - 1:
                output = output + ","
        output = output + "\n"
    return output


def filter_rows(rows, column, value):
    result = []
    for row in rows:
        if column in row and row[column] == value:
            result.append(row)
    return result


def sort_rows(rows, column, reverse=False):
    # Bubble sort (intentionally bad)
    sorted_rows = list(rows)
    for i in range(len(sorted_rows)):
        for j in range(0, len(sorted_rows) - i - 1):
            a = sorted_rows[j].get(column, "")
            b = sorted_rows[j + 1].get(column, "")
            if reverse:
                if a < b:
                    sorted_rows[j], sorted_rows[j + 1] = sorted_rows[j + 1], sorted_rows[j]
            else:
                if a > b:
                    sorted_rows[j], sorted_rows[j + 1] = sorted_rows[j + 1], sorted_rows[j]
    return sorted_rows
