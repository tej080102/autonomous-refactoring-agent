import pytest
from sample_09_matrix import (
    make_matrix, add_matrices, multiply_matrices, transpose,
    determinant_2x2, flatten, sum_matrix, scalar_multiply, identity
)


class TestMakeMatrix:
    def test_basic(self):
        m = make_matrix(2, 3)
        assert len(m) == 2
        assert len(m[0]) == 3
        assert m[0][0] == 0

    def test_fill(self):
        m = make_matrix(2, 2, fill=5)
        assert m[0][0] == 5
        assert m[1][1] == 5


class TestAddMatrices:
    def test_basic(self):
        a = [[1, 2], [3, 4]]
        b = [[5, 6], [7, 8]]
        result = add_matrices(a, b)
        assert result == [[6, 8], [10, 12]]


class TestMultiplyMatrices:
    def test_basic(self):
        a = [[1, 2], [3, 4]]
        b = [[5, 6], [7, 8]]
        result = multiply_matrices(a, b)
        assert result == [[19, 22], [43, 50]]

    def test_identity(self):
        a = [[1, 2], [3, 4]]
        i = identity(2)
        assert multiply_matrices(a, i) == a


class TestTranspose:
    def test_square(self):
        m = [[1, 2], [3, 4]]
        assert transpose(m) == [[1, 3], [2, 4]]

    def test_rectangular(self):
        m = [[1, 2, 3], [4, 5, 6]]
        t = transpose(m)
        assert len(t) == 3
        assert len(t[0]) == 2


class TestDeterminant:
    def test_basic(self):
        assert determinant_2x2([[1, 2], [3, 4]]) == -2

    def test_identity(self):
        assert determinant_2x2([[1, 0], [0, 1]]) == 1


class TestFlatten:
    def test_basic(self):
        assert flatten([[1, 2], [3, 4]]) == [1, 2, 3, 4]


class TestSumMatrix:
    def test_basic(self):
        assert sum_matrix([[1, 2], [3, 4]]) == 10


class TestScalarMultiply:
    def test_basic(self):
        result = scalar_multiply([[1, 2], [3, 4]], 3)
        assert result == [[3, 6], [9, 12]]


class TestIdentity:
    def test_2x2(self):
        assert identity(2) == [[1, 0], [0, 1]]

    def test_3x3(self):
        i = identity(3)
        assert i[0][0] == 1
        assert i[1][1] == 1
        assert i[0][1] == 0
