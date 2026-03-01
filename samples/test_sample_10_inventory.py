import pytest
from sample_10_inventory import Inventory


class TestInventory:
    def setup_method(self):
        self.inv = Inventory()
        self.inv.add_product("Laptop", "Electronics", 999.99, 10)
        self.inv.add_product("Mouse", "Electronics", 29.99, 50)
        self.inv.add_product("Desk", "Furniture", 199.99, 5)

    def test_add(self):
        assert len(self.inv.products) == 3

    def test_find_by_name(self):
        p = self.inv.find_by_name("laptop")
        assert p is not None
        assert p["price"] == 999.99

    def test_find_missing(self):
        assert self.inv.find_by_name("Phone") is None

    def test_find_by_category(self):
        assert len(self.inv.find_by_category("electronics")) == 2

    def test_search(self):
        assert len(self.inv.search("lap")) == 1

    def test_update_stock(self):
        self.inv.update_stock("Laptop", -3)
        assert self.inv.find_by_name("Laptop")["stock"] == 7

    def test_update_stock_clamp(self):
        self.inv.update_stock("Desk", -100)
        assert self.inv.find_by_name("Desk")["stock"] == 0

    def test_update_missing(self):
        assert self.inv.update_stock("Phone", 5) is False

    def test_low_stock(self):
        low = self.inv.get_low_stock()
        assert len(low) == 1
        assert low[0]["name"] == "Desk"

    def test_total_value(self):
        expected = 999.99 * 10 + 29.99 * 50 + 199.99 * 5
        assert abs(self.inv.get_total_value() - expected) < 0.01

    def test_category_summary(self):
        summary = self.inv.get_category_summary()
        assert summary["Electronics"]["count"] == 2
        assert summary["Furniture"]["count"] == 1

    def test_remove_product(self):
        assert self.inv.remove_product("Mouse") is True
        assert len(self.inv.products) == 2

    def test_remove_missing(self):
        assert self.inv.remove_product("Phone") is False

    def test_apply_discount(self):
        count = self.inv.apply_discount("Electronics", 10)
        assert count == 2
        assert abs(self.inv.find_by_name("Laptop")["price"] - 899.991) < 0.01

    def test_report(self):
        report = self.inv.get_report()
        assert "INVENTORY REPORT" in report
        assert "Laptop" in report
        assert "Total Value" in report

    def test_empty_inventory(self):
        inv = Inventory()
        assert inv.get_total_value() == 0
        assert inv.get_category_summary() == {}
