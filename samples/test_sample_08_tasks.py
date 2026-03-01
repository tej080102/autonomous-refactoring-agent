import pytest
from sample_08_tasks import TaskManager


class TestTaskManager:
    def setup_method(self):
        self.tm = TaskManager()
        self.tm.add_task("Buy groceries", "low")
        self.tm.add_task("Finish report", "high")
        self.tm.add_task("Call dentist", "medium")

    def test_add_task(self):
        assert len(self.tm.tasks) == 3

    def test_ids_increment(self):
        ids = [t["id"] for t in self.tm.tasks]
        assert ids == [1, 2, 3]

    def test_complete_task(self):
        assert self.tm.complete_task(1) is True
        assert self.tm.tasks[0]["completed"] is True

    def test_complete_missing(self):
        assert self.tm.complete_task(99) is False

    def test_get_pending(self):
        self.tm.complete_task(1)
        assert len(self.tm.get_pending()) == 2

    def test_get_completed(self):
        self.tm.complete_task(1)
        assert len(self.tm.get_completed()) == 1

    def test_get_by_priority(self):
        assert len(self.tm.get_by_priority("high")) == 1

    def test_high_priority_pending(self):
        assert len(self.tm.get_high_priority_pending()) == 1
        self.tm.complete_task(2)
        assert len(self.tm.get_high_priority_pending()) == 0

    def test_stats(self):
        self.tm.complete_task(1)
        stats = self.tm.get_stats()
        assert stats["total"] == 3
        assert stats["completed"] == 1
        assert stats["pending"] == 2
        assert abs(stats["completion_rate"] - 1/3) < 0.01

    def test_stats_empty(self):
        tm = TaskManager()
        assert tm.get_stats()["completion_rate"] == 0

    def test_delete_task(self):
        assert self.tm.delete_task(2) is True
        assert len(self.tm.tasks) == 2

    def test_delete_missing(self):
        assert self.tm.delete_task(99) is False

    def test_search(self):
        results = self.tm.search("groceries")
        assert len(results) == 1
        assert results[0]["title"] == "Buy groceries"

    def test_search_case_insensitive(self):
        assert len(self.tm.search("REPORT")) == 1

    def test_search_no_match(self):
        assert self.tm.search("xyz") == []
