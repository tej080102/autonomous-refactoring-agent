import pytest
from sample_02_strings import chk, chk2, fmt, fmt_table, count_words


class TestChk:
    def test_valid(self):
        assert chk("hello") is True

    def test_none(self):
        assert chk(None) is False

    def test_empty(self):
        assert chk("") is False

    def test_too_long(self):
        assert chk("a" * 256) is False

    def test_max_length(self):
        assert chk("a" * 255) is True


class TestChk2:
    def test_valid_alnum(self):
        assert chk2("hello_world") is True

    def test_none(self):
        assert chk2(None) is False

    def test_special_chars(self):
        assert chk2("hello@world") is False

    def test_underscore_ok(self):
        assert chk2("a_b_c") is True


class TestFmt:
    def test_single(self):
        assert fmt([1]) == "1"

    def test_multiple(self):
        assert fmt([1, 2, 3]) == "1, 2, 3"

    def test_empty(self):
        assert fmt([]) == ""

    def test_strings(self):
        assert fmt(["a", "b"]) == "a, b"


class TestFmtTable:
    def test_basic_table(self):
        result = fmt_table(["Name", "Age"], [["Alice", 30], ["Bob", 25]])
        assert "Name | Age" in result
        assert "Alice | 30" in result
        assert "--- | ---" in result

    def test_single_col(self):
        result = fmt_table(["X"], [["1"], ["2"]])
        assert "X\n" in result


class TestCountWords:
    def test_basic(self):
        assert count_words("hello hello world") == {"hello": 2, "world": 1}

    def test_none(self):
        assert count_words(None) == {}

    def test_punctuation_stripped(self):
        result = count_words("hello, hello!")
        assert result == {"hello": 2}

    def test_case_insensitive(self):
        result = count_words("Hello hello")
        assert result == {"hello": 2}
