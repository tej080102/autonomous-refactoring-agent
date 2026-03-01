import pytest
from sample_06_cart import Cart


class TestCart:
    def setup_method(self):
        self.cart = Cart()
        self.cart.add("Apple", 1.50, 3)
        self.cart.add("Bread", 2.00, 1)

    def test_add_item(self):
        assert len(self.cart.items) == 2

    def test_subtotal(self):
        assert self.cart.get_subtotal() == 6.50

    def test_total_no_discount(self):
        assert self.cart.get_total() == 6.50

    def test_discount_10(self):
        self.cart.apply_discount("SAVE10")
        assert self.cart.get_total() == pytest.approx(5.85)

    def test_discount_20(self):
        self.cart.apply_discount("SAVE20")
        assert self.cart.get_total() == pytest.approx(5.20)

    def test_discount_half(self):
        self.cart.apply_discount("HALF")
        assert self.cart.get_total() == pytest.approx(3.25)

    def test_invalid_discount(self):
        self.cart.apply_discount("FAKE")
        assert self.cart.get_total() == 6.50

    def test_remove_item(self):
        self.cart.remove("Apple")
        assert len(self.cart.items) == 1
        assert self.cart.get_subtotal() == 2.00

    def test_item_count(self):
        assert self.cart.get_item_count() == 4

    def test_find_item(self):
        item = self.cart.find_item("Apple")
        assert item is not None
        assert item["price"] == 1.50

    def test_find_missing(self):
        assert self.cart.find_item("Missing") is None

    def test_update_qty(self):
        self.cart.update_qty("Apple", 5)
        assert self.cart.find_item("Apple")["qty"] == 5

    def test_update_missing(self):
        assert self.cart.update_qty("Missing", 1) is False

    def test_summary(self):
        summary = self.cart.get_summary()
        assert "Apple" in summary
        assert "Total" in summary

    def test_empty_cart(self):
        c = Cart()
        assert c.get_subtotal() == 0
        assert c.get_total() == 0
        assert c.get_item_count() == 0
