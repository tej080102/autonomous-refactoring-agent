import pytest
from sample_07_auth import check_password, check_username, generate_token, mask_email, mask_phone


class TestCheckPassword:
    def test_valid(self):
        result = check_password("Str0ng!Pass")
        assert result["valid"] is True

    def test_none(self):
        result = check_password(None)
        assert result["valid"] is False

    def test_too_short(self):
        result = check_password("Ab1!")
        assert result["valid"] is False
        assert any("8 characters" in e for e in result["errors"])

    def test_no_uppercase(self):
        result = check_password("abcdefg1!")
        assert result["valid"] is False

    def test_no_digit(self):
        result = check_password("Abcdefgh!")
        assert result["valid"] is False

    def test_no_special(self):
        result = check_password("Abcdefg1x")
        assert result["valid"] is False


class TestCheckUsername:
    def test_valid(self):
        result = check_username("alice_01")
        assert result["valid"] is True

    def test_none(self):
        result = check_username(None)
        assert result["valid"] is False

    def test_too_short(self):
        result = check_username("ab")
        assert result["valid"] is False

    def test_starts_with_digit(self):
        result = check_username("1alice")
        assert result["valid"] is False

    def test_special_chars(self):
        result = check_username("alice@bob")
        assert result["valid"] is False


class TestGenerateToken:
    def test_returns_hex(self):
        token = generate_token("alice", "admin")
        assert len(token) == 64
        assert all(c in "0123456789abcdef" for c in token)

    def test_different_inputs(self):
        t1 = generate_token("alice", "admin")
        t2 = generate_token("bob", "user")
        assert t1 != t2


class TestMaskEmail:
    def test_basic(self):
        assert mask_email("alice@example.com") == "a***e@example.com"

    def test_short_name(self):
        assert mask_email("ab@x.com") == "a*@x.com"

    def test_none(self):
        assert mask_email(None) == ""

    def test_no_at(self):
        assert mask_email("invalid") == ""


class TestMaskPhone:
    def test_basic(self):
        assert mask_phone("555-1234") == "***1234"

    def test_formatted(self):
        assert mask_phone("(555) 123-4567") == "******4567"

    def test_none(self):
        assert mask_phone(None) == ""

    def test_short(self):
        assert mask_phone("123") == "****"
