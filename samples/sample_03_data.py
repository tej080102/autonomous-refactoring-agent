"""
Sample 3: Data processing with nested loops and poor error handling.
Issues: deeply nested code, bare excepts, god function, no type hints.
"""


def process_records(records):
    results = []
    errors = []
    for record in records:
        try:
            name = record["name"]
            age = record["age"]
            email = record["email"]

            # Validate name
            if name == None or name == "":
                errors.append("Invalid name")
                continue

            # Validate age
            try:
                age = int(age)
            except:
                errors.append("Invalid age for " + name)
                continue

            if age < 0 or age > 150:
                errors.append("Age out of range for " + name)
                continue

            # Validate email
            if email == None or "@" not in email:
                errors.append("Invalid email for " + name)
                continue

            results.append({
                "name": name,
                "age": age,
                "email": email,
                "category": "senior" if age >= 65 else "adult" if age >= 18 else "minor"
            })
        except:
            errors.append("Unknown error processing record")

    return {"results": results, "errors": errors, "total": len(results)}


def summarize(records):
    processed = process_records(records)
    results = processed["results"]

    if len(results) == 0:
        return {"count": 0, "avg_age": 0, "categories": {}}

    total_age = 0
    categories = {}
    for r in results:
        total_age = total_age + r["age"]
        cat = r["category"]
        if cat in categories:
            categories[cat] = categories[cat] + 1
        else:
            categories[cat] = 1

    return {
        "count": len(results),
        "avg_age": total_age / len(results),
        "categories": categories
    }


def find_duplicates(records):
    seen_emails = {}
    duplicates = []
    for record in records:
        try:
            email = record.get("email", "").lower()
            if email in seen_emails:
                duplicates.append(email)
            else:
                seen_emails[email] = True
        except:
            pass
    return duplicates
