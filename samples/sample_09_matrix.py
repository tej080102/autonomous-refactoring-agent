"""
Sample 9: Matrix operations implemented manually.
Issues: deeply nested loops, no type hints, duplicated iteration,
        magic numbers, no input validation.
"""


def make_matrix(rows, cols, fill=0):
    m = []
    for i in range(rows):
        row = []
        for j in range(cols):
            row.append(fill)
        m.append(row)
    return m


def add_matrices(a, b):
    rows = len(a)
    cols = len(a[0])
    result = make_matrix(rows, cols)
    for i in range(rows):
        for j in range(cols):
            result[i][j] = a[i][j] + b[i][j]
    return result


def multiply_matrices(a, b):
    rows_a = len(a)
    cols_a = len(a[0])
    cols_b = len(b[0])
    result = make_matrix(rows_a, cols_b)
    for i in range(rows_a):
        for j in range(cols_b):
            total = 0
            for k in range(cols_a):
                total = total + a[i][k] * b[k][j]
            result[i][j] = total
    return result


def transpose(m):
    rows = len(m)
    cols = len(m[0])
    result = make_matrix(cols, rows)
    for i in range(rows):
        for j in range(cols):
            result[j][i] = m[i][j]
    return result


def determinant_2x2(m):
    return m[0][0] * m[1][1] - m[0][1] * m[1][0]


def flatten(m):
    result = []
    for row in m:
        for val in row:
            result.append(val)
    return result


def sum_matrix(m):
    total = 0
    for row in m:
        for val in row:
            total = total + val
    return total


def scalar_multiply(m, scalar):
    rows = len(m)
    cols = len(m[0])
    result = make_matrix(rows, cols)
    for i in range(rows):
        for j in range(cols):
            result[i][j] = m[i][j] * scalar
    return result


def identity(n):
    m = make_matrix(n, n)
    for i in range(n):
        m[i][i] = 1
    return m
