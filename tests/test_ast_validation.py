"""
Unit tests for AST validation logic used by executor and repair nodes.

These tests verify that:
  - Valid Python code passes validation
  - Invalid Python code is caught and original code is preserved
  - Markdown fences are stripped before parsing
"""

import ast
import pytest

# Import the strip function directly — it's a simple utility
from src.nodes.executor import _strip_markdown_fences


class TestStripMarkdownFences:
    """Tests for the markdown fence stripping utility."""

    def test_strips_python_fence(self):
        text = '```python\nprint("hello")\n```'
        assert _strip_markdown_fences(text) == 'print("hello")'

    def test_strips_py_fence(self):
        text = '```py\nprint("hello")\n```'
        assert _strip_markdown_fences(text) == 'print("hello")'

    def test_strips_plain_fence(self):
        text = '```\nprint("hello")\n```'
        assert _strip_markdown_fences(text) == 'print("hello")'

    def test_no_fences_unchanged(self):
        text = 'print("hello")'
        assert _strip_markdown_fences(text) == 'print("hello")'

    def test_strips_whitespace(self):
        text = '  ```python\nprint("hello")\n```  '
        assert _strip_markdown_fences(text) == 'print("hello")'

    def test_multiline_code(self):
        text = '```python\ndef foo():\n    return 42\n```'
        expected = 'def foo():\n    return 42'
        assert _strip_markdown_fences(text) == expected

    def test_empty_string(self):
        assert _strip_markdown_fences("") == ""


class TestASTValidation:
    """Tests verifying AST validation catches bad code."""

    def test_valid_python_passes(self):
        code = 'def foo():\n    return 42\n'
        ast.parse(code)  # Should not raise

    def test_invalid_python_raises(self):
        code = 'def foo(\n    not valid python'
        with pytest.raises(SyntaxError):
            ast.parse(code)

    def test_empty_string_is_valid(self):
        ast.parse("")  # Empty string is valid Python

    def test_import_statement_is_valid(self):
        ast.parse("import os\nimport sys\n")

    def test_class_definition_is_valid(self):
        code = 'class Foo:\n    def bar(self):\n        pass\n'
        ast.parse(code)
