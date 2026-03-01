"""
Tests for messy_utils.py — these must pass before AND after refactoring.

The refactoring agent uses these tests to verify that its changes don't
break functionality. Covers all public functions.
"""

import pytest
from messy_utils import do_stuff, do_more_stuff, process, handle, calc


# -----------------------------------------------------------------------
# do_stuff
# -----------------------------------------------------------------------

class TestDoStuff:
    def test_basic_addition(self):
        assert do_stuff(2, 3) == 5

    def test_large_result_doubles(self):
        # 60 + 50 = 110 > 100, so doubled → 220
        assert do_stuff(60, 50) == 220

    def test_negative_result_clamps_to_zero(self):
        assert do_stuff(-10, -5) == 0

    def test_boundary_at_100(self):
        # 50 + 50 = 100, NOT > 100, so no doubling
        assert do_stuff(50, 50) == 100

    def test_boundary_at_101(self):
        # 51 + 50 = 101 > 100, doubled → 202
        assert do_stuff(51, 50) == 202

    def test_zero_result(self):
        assert do_stuff(0, 0) == 0


# -----------------------------------------------------------------------
# do_more_stuff
# -----------------------------------------------------------------------

class TestDoMoreStuff:
    def test_basic(self):
        # (2 + 3) = 5 → 5 * 3 = 15
        assert do_more_stuff(2, 3) == 15

    def test_large_result_doubles_then_triples(self):
        # 60 + 50 = 110 > 100 → 220 * 3 = 660
        assert do_more_stuff(60, 50) == 660

    def test_negative_clamps_then_triples(self):
        # -10 + -5 = -15 < 0 → 0 * 3 = 0
        assert do_more_stuff(-10, -5) == 0


# -----------------------------------------------------------------------
# process
# -----------------------------------------------------------------------

class TestProcess:
    def test_basic_stats(self):
        result = process([10, 20, 30])
        assert result["total"] == 60
        assert result["count"] == 3
        assert result["average"] == 20.0
        assert result["min"] == 10
        assert result["max"] == 30

    def test_grade_a(self):
        result = process([95, 92, 90])
        assert result["grade"] == "A"

    def test_grade_b(self):
        result = process([85, 82, 80])
        assert result["grade"] == "B"

    def test_grade_c(self):
        result = process([75, 72, 70])
        assert result["grade"] == "C"

    def test_grade_d(self):
        result = process([65, 62, 60])
        assert result["grade"] == "D"

    def test_grade_f(self):
        result = process([50, 40, 30])
        assert result["grade"] == "F"

    def test_empty_list(self):
        result = process([])
        assert result["count"] == 0
        assert result["average"] == 0
        assert result["min"] is None
        assert result["max"] is None

    def test_non_numeric_items_skipped(self):
        result = process([10, "abc", 20, None, 30])
        assert result["count"] == 3
        assert result["total"] == 60

    def test_string_numbers_accepted(self):
        result = process(["10", "20", "30"])
        assert result["total"] == 60.0


# -----------------------------------------------------------------------
# handle
# -----------------------------------------------------------------------

class TestHandle:
    def test_spaces_to_underscores(self):
        assert handle("hello world") == "hello_world"

    def test_tabs_to_four_underscores(self):
        assert handle("a\tb") == "a____b"

    def test_newlines_escaped(self):
        assert handle("line1\nline2") == "line1\\nline2"

    def test_none_returns_empty(self):
        assert handle(None) == ""

    def test_empty_string(self):
        assert handle("") == ""

    def test_no_special_chars(self):
        assert handle("hello") == "hello"

    def test_mixed_whitespace(self):
        assert handle("a b\tc\nd") == "a_b____c\\nd"


# -----------------------------------------------------------------------
# calc
# -----------------------------------------------------------------------

class TestCalc:
    def test_basic_calculation(self):
        result = calc(1, 2, 3, 4)
        assert result["sum"] == 10
        assert result["product"] == 24
        assert result["average"] == 2.5
        assert result["max"] == 4
        assert result["min"] == 1
        assert result["range"] == 3

    def test_all_same_values(self):
        result = calc(5, 5, 5, 5)
        assert result["sum"] == 20
        assert result["product"] == 625
        assert result["average"] == 5.0
        assert result["max"] == 5
        assert result["min"] == 5
        assert result["range"] == 0

    def test_negative_values(self):
        result = calc(-1, -2, -3, -4)
        assert result["sum"] == -10
        assert result["max"] == -1
        assert result["min"] == -4
        assert result["range"] == 3

    def test_mixed_values(self):
        result = calc(-10, 0, 5, 10)
        assert result["sum"] == 5
        assert result["max"] == 10
        assert result["min"] == -10
        assert result["range"] == 20

    def test_zeros(self):
        result = calc(0, 0, 0, 0)
        assert result["sum"] == 0
        assert result["product"] == 0
        assert result["average"] == 0.0
        assert result["range"] == 0
