"""
Sample 10: Inventory system with multiple anti-patterns.
Issues: god class, no type hints, duplicated search logic,
        string formatting with concatenation, manual aggregation.
"""


class Inventory:
    def __init__(self):
        self.products = []

    def add_product(self, name, category, price, stock):
        p = {
            "name": name,
            "category": category,
            "price": price,
            "stock": stock,
        }
        self.products.append(p)

    def find_by_name(self, name):
        for p in self.products:
            if p["name"].lower() == name.lower():
                return p
        return None

    def find_by_category(self, category):
        result = []
        for p in self.products:
            if p["category"].lower() == category.lower():
                result.append(p)
        return result

    def search(self, keyword):
        result = []
        for p in self.products:
            if keyword.lower() in p["name"].lower():
                result.append(p)
        return result

    def update_stock(self, name, amount):
        for p in self.products:
            if p["name"].lower() == name.lower():
                p["stock"] = p["stock"] + amount
                if p["stock"] < 0:
                    p["stock"] = 0
                return True
        return False

    def get_low_stock(self, threshold=5):
        result = []
        for p in self.products:
            if p["stock"] <= threshold:
                result.append(p)
        return result

    def get_total_value(self):
        total = 0
        for p in self.products:
            total = total + p["price"] * p["stock"]
        return total

    def get_category_summary(self):
        categories = {}
        for p in self.products:
            cat = p["category"]
            if cat not in categories:
                categories[cat] = {"count": 0, "total_value": 0, "total_stock": 0}
            categories[cat]["count"] = categories[cat]["count"] + 1
            categories[cat]["total_value"] = categories[cat]["total_value"] + p["price"] * p["stock"]
            categories[cat]["total_stock"] = categories[cat]["total_stock"] + p["stock"]
        return categories

    def remove_product(self, name):
        new_products = []
        found = False
        for p in self.products:
            if p["name"].lower() == name.lower():
                found = True
            else:
                new_products.append(p)
        self.products = new_products
        return found

    def apply_discount(self, category, percent):
        count = 0
        for p in self.products:
            if p["category"].lower() == category.lower():
                p["price"] = p["price"] * (1 - percent / 100)
                count = count + 1
        return count

    def get_report(self):
        output = "INVENTORY REPORT\n"
        output = output + "=" * 40 + "\n"
        for p in self.products:
            output = output + p["name"] + " (" + p["category"] + ")"
            output = output + " - $" + str(p["price"])
            output = output + " x " + str(p["stock"])
            output = output + " = $" + str(p["price"] * p["stock"]) + "\n"
        output = output + "=" * 40 + "\n"
        output = output + "Total Value: $" + str(self.get_total_value()) + "\n"
        return output
