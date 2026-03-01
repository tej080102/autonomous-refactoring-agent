"""
Sample 7: Password/auth utilities with security anti-patterns.
Issues: hardcoded values, no type hints, duplicated validation,
        poor error messages, string concatenation.
"""


def check_password(password):
    if password == None:
        return {"valid": False, "errors": ["Password is required"]}

    errors = []
    if len(password) < 8:
        errors.append("Password must be at least 8 characters")
    if len(password) > 64:
        errors.append("Password must be at most 64 characters")

    has_upper = False
    has_lower = False
    has_digit = False
    has_special = False

    for c in password:
        if c.isupper():
            has_upper = True
        if c.islower():
            has_lower = True
        if c.isdigit():
            has_digit = True
        if c in "!@#$%^&*()_+-=[]{}|;:,.<>?":
            has_special = True

    if not has_upper:
        errors.append("Password must contain uppercase letter")
    if not has_lower:
        errors.append("Password must contain lowercase letter")
    if not has_digit:
        errors.append("Password must contain digit")
    if not has_special:
        errors.append("Password must contain special character")

    return {"valid": len(errors) == 0, "errors": errors}


def check_username(username):
    if username == None:
        return {"valid": False, "errors": ["Username is required"]}

    errors = []
    if len(username) < 3:
        errors.append("Username must be at least 3 characters")
    if len(username) > 32:
        errors.append("Username must be at most 32 characters")

    for c in username:
        if not c.isalnum() and c != "_" and c != "-":
            errors.append("Username contains invalid character: " + c)
            break

    if username[0].isdigit():
        errors.append("Username cannot start with a digit")

    return {"valid": len(errors) == 0, "errors": errors}


def generate_token(username, role):
    import hashlib
    import time
    raw = username + ":" + role + ":" + str(int(time.time()))
    token = hashlib.sha256(raw.encode()).hexdigest()
    return token


def mask_email(email):
    if email == None or "@" not in email:
        return ""
    parts = email.split("@")
    name = parts[0]
    domain = parts[1]
    if len(name) <= 2:
        masked = name[0] + "*" * (len(name) - 1)
    else:
        masked = name[0] + "*" * (len(name) - 2) + name[-1]
    return masked + "@" + domain


def mask_phone(phone):
    if phone == None:
        return ""
    digits = ""
    for c in phone:
        if c.isdigit():
            digits = digits + c
    if len(digits) < 4:
        return "****"
    return "*" * (len(digits) - 4) + digits[-4:]
