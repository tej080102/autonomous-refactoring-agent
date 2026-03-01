import pytest
from sample_04_csv import parse_csv_line, parse_csv, to_csv, filter_rows, sort_rows


class TestParseCsvLine:
    def test_simple(self):
        assert parse_csv_line("a,b,c") == ["a", "b", "c"]

    def test_with_quotes(self):
        assert parse_csv_line('a,"b,c",d') == ["a", "b,c", "d"]

    def test_whitespace(self):
        assert parse_csv_line("a , b , c") == ["a", "b", "c"]

    def test_single(self):
        assert parse_csv_line("hello") == ["hello"]


class TestParseCsv:
    def test_basic(self):
        csv = "name,age\nAlice,30\nBob,25"
        rows = parse_csv(csv)
        assert len(rows) == 2
        assert rows[0]["name"] == "Alice"
        assert rows[1]["age"] == "25"

    def test_missing_values(self):
        csv = "a,b,c\n1,2"
        rows = parse_csv(csv)
        assert rows[0]["c"] == ""

    def test_empty(self):
        assert parse_csv("") == []


class TestToCsv:
    def test_basic(self):
        result = to_csv(["name", "age"], [{"name": "Alice", "age": 30}])
        assert "name,age" in result
        assert "Alice,30" in result

    def test_value_with_comma(self):
        result = to_csv(["name"], [{"name": "A, B"}])
        assert '"A, B"' in result


class TestFilterRows:
    def test_match(self):
        rows = [{"x": "a"}, {"x": "b"}, {"x": "a"}]
        assert len(filter_rows(rows, "x", "a")) == 2

    def test_no_match(self):
        rows = [{"x": "a"}]
        assert filter_rows(rows, "x", "z") == []


class TestSortRows:
    def test_ascending(self):
        rows = [{"x": "c"}, {"x": "a"}, {"x": "b"}]
        sorted_r = sort_rows(rows, "x")
        assert [r["x"] for r in sorted_r] == ["a", "b", "c"]

    def test_descending(self):
        rows = [{"x": "a"}, {"x": "c"}, {"x": "b"}]
        sorted_r = sort_rows(rows, "x", reverse=True)
        assert [r["x"] for r in sorted_r] == ["c", "b", "a"]
