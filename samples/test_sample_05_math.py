import pytest
from sample_05_math import m, md, sd, pct, describe


class TestMean:
    def test_basic(self):
        assert m([1, 2, 3]) == 2.0

    def test_single(self):
        assert m([5]) == 5.0

    def test_empty(self):
        assert m([]) == 0


class TestMedian:
    def test_odd(self):
        assert md([3, 1, 2]) == 2

    def test_even(self):
        assert md([1, 2, 3, 4]) == 2.5

    def test_single(self):
        assert md([7]) == 7

    def test_empty(self):
        assert md([]) == 0


class TestStdDev:
    def test_uniform(self):
        assert sd([5, 5, 5]) == 0.0

    def test_basic(self):
        result = sd([2, 4, 4, 4, 5, 5, 7, 9])
        assert abs(result - 2.0) < 0.01

    def test_empty(self):
        assert sd([]) == 0


class TestPercentile:
    def test_p50_is_median(self):
        data = [1, 2, 3, 4, 5]
        assert pct(data, 50) == md(data)

    def test_p0(self):
        assert pct([1, 2, 3], 0) == 1

    def test_p100(self):
        assert pct([1, 2, 3], 100) == 3

    def test_empty(self):
        assert pct([], 50) == 0


class TestDescribe:
    def test_basic(self):
        result = describe([1, 2, 3, 4, 5])
        assert result["count"] == 5
        assert result["mean"] == 3.0
        assert result["median"] == 3
        assert result["min"] == 1
        assert result["max"] == 5
