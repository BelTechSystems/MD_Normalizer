"""Tests for Markdown validation."""

from mdnorm.validator import validate


def test_valid_document_passes() -> None:
    result = validate("# Title\n\nBody paragraph.\n")

    assert result.ok is True
    assert result.errors == []
    assert result.warnings == []


def test_empty_document_error() -> None:
    result = validate("\n\n")

    assert result.ok is False
    assert any(error.message == "Document is empty." for error in result.errors)


def test_unclosed_code_fence_error() -> None:
    result = validate("# Title\n\n```python\nprint('hi')\n")

    assert result.ok is False
    assert any(
        error.message == "Unclosed fenced code block." and error.line_number == 3
        for error in result.errors
    )


def test_malformed_heading_error() -> None:
    result = validate("#Title without space\n")

    assert result.ok is False
    assert any(
        error.message == "Malformed heading." and error.line_number == 1
        for error in result.errors
    )


def test_trailing_whitespace_error_outside_code_blocks() -> None:
    result = validate("Paragraph with spaces   \n")

    assert result.ok is False
    assert any(
        error.message == "Trailing whitespace is not allowed."
        and error.line_number == 1
        for error in result.errors
    )


def test_trailing_whitespace_allowed_in_code_blocks() -> None:
    result = validate("```\ncode with spaces   \n```\n")

    trailing_errors = [
        error
        for error in result.errors
        if error.message == "Trailing whitespace is not allowed."
    ]
    assert trailing_errors == []


def test_heading_jump_warning() -> None:
    result = validate("# Title\n\n### Skipped level\n")

    assert result.ok is True
    assert any(
        warning.message == "Heading level jumps from 1 to 3."
        and warning.line_number == 3
        for warning in result.warnings
    )
