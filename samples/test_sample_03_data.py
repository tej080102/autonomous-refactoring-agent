import pytest
from sample_03_data import process_records, summarize, find_duplicates


VALID_RECORDS = [
    {"name": "Alice", "age": 30, "email": "alice@test.com"},
    {"name": "Bob", "age": 70, "email": "bob@test.com"},
    {"name": "Charlie", "age": 10, "email": "charlie@test.com"},
]


class TestProcessRecords:
    def test_valid_records(self):
        result = process_records(VALID_RECORDS)
        assert result["total"] == 3
        assert len(result["errors"]) == 0

    def test_invalid_name(self):
        result = process_records([{"name": "", "age": 25, "email": "x@y.com"}])
        assert result["total"] == 0
        assert len(result["errors"]) == 1

    def test_invalid_age(self):
        result = process_records([{"name": "A", "age": "abc", "email": "x@y.com"}])
        assert result["total"] == 0

    def test_age_out_of_range(self):
        result = process_records([{"name": "A", "age": 200, "email": "x@y.com"}])
        assert result["total"] == 0

    def test_invalid_email(self):
        result = process_records([{"name": "A", "age": 25, "email": "no-at"}])
        assert result["total"] == 0

    def test_category_senior(self):
        result = process_records([{"name": "A", "age": 70, "email": "a@b.com"}])
        assert result["results"][0]["category"] == "senior"

    def test_category_minor(self):
        result = process_records([{"name": "A", "age": 10, "email": "a@b.com"}])
        assert result["results"][0]["category"] == "minor"

    def test_missing_key(self):
        result = process_records([{"name": "A"}])
        assert result["total"] == 0

    def test_empty_list(self):
        result = process_records([])
        assert result["total"] == 0


class TestSummarize:
    def test_basic(self):
        result = summarize(VALID_RECORDS)
        assert result["count"] == 3
        assert abs(result["avg_age"] - 36.67) < 0.1

    def test_categories(self):
        result = summarize(VALID_RECORDS)
        assert result["categories"]["adult"] == 1
        assert result["categories"]["senior"] == 1
        assert result["categories"]["minor"] == 1

    def test_empty(self):
        result = summarize([])
        assert result["count"] == 0
        assert result["avg_age"] == 0


class TestFindDuplicates:
    def test_no_duplicates(self):
        assert find_duplicates(VALID_RECORDS) == []

    def test_with_duplicates(self):
        records = VALID_RECORDS + [{"name": "D", "age": 25, "email": "alice@test.com"}]
        assert "alice@test.com" in find_duplicates(records)

    def test_case_insensitive(self):
        records = [
            {"name": "A", "age": 25, "email": "X@Y.com"},
            {"name": "B", "age": 30, "email": "x@y.com"},
        ]
        assert len(find_duplicates(records)) == 1
