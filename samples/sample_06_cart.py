"""
Sample 6: Shopping cart with OOP anti-patterns.
Issues: no encapsulation, duplicated discount logic, no type hints,
        mutable default args, manual iteration patterns.
"""


class Cart:
    def __init__(self):
        self.items = []
        self.discount_code = None

    def add(self, name, price, qty):
        self.items.append({"name": name, "price": price, "qty": qty})

    def remove(self, name):
        new_items = []
        for item in self.items:
            if item["name"] != name:
                new_items.append(item)
        self.items = new_items

    def get_subtotal(self):
        total = 0
        for item in self.items:
            total = total + item["price"] * item["qty"]
        return total

    def apply_discount(self, code):
        self.discount_code = code

    def get_total(self):
        subtotal = 0
        for item in self.items:
            subtotal = subtotal + item["price"] * item["qty"]

        if self.discount_code == "SAVE10":
            discount = subtotal * 0.10
        elif self.discount_code == "SAVE20":
            discount = subtotal * 0.20
        elif self.discount_code == "HALF":
            discount = subtotal * 0.50
        else:
            discount = 0

        return subtotal - discount

    def get_item_count(self):
        count = 0
        for item in self.items:
            count = count + item["qty"]
        return count

    def get_summary(self):
        lines = []
        for item in self.items:
            line = item["name"] + " x" + str(item["qty"]) + " = $" + str(item["price"] * item["qty"])
            lines.append(line)
        lines.append("Subtotal: $" + str(self.get_subtotal()))
        lines.append("Total: $" + str(self.get_total()))
        return "\n".join(lines)

    def find_item(self, name):
        for item in self.items:
            if item["name"] == name:
                return item
        return None

    def update_qty(self, name, qty):
        for item in self.items:
            if item["name"] == name:
                item["qty"] = qty
                return True
        return False
