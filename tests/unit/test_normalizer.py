"""Tests for deterministic Markdown normalization."""

from mdnorm.normalizer import normalize


def test_trailing_whitespace_removed_outside_code_blocks() -> None:
    source = "Paragraph with spaces   \n\n# Heading   \n"
    output, report = normalize(source)

    assert output == "Paragraph with spaces\n\n# Heading\n"
    assert any(change.rule == "trailing_whitespace" for change in report.changes)


def test_code_block_content_unchanged() -> None:
    source = "Text   \n\n```python\nline with spaces   \n# not heading\n```   \n"
    output, _report = normalize(source)

    assert "line with spaces   \n" in output
    assert "# not heading\n" in output
    assert "```   \n" in output
    assert "```python\n" in output
    assert "Text   \n" not in output


def test_bullet_marker_normalization() -> None:
    source = "* first\n+ second\n- third\n"
    output, report = normalize(source)

    assert output == "- first\n- second\n- third\n"
    assert sum(change.rule == "unordered_list_marker" for change in report.changes) == 2


def test_ordered_list_normalization() -> None:
    source = "3. third\n5) fifth\n7. seventh\n"
    output, report = normalize(source)

    assert output == "1. third\n2. fifth\n3. seventh\n"
    assert any(change.rule == "ordered_list_number" for change in report.changes)


def test_heading_blank_line_normalization() -> None:
    source = "Intro\n# Title\nBody\n## Section\nMore\n"
    output, report = normalize(source)

    assert output == "Intro\n\n# Title\n\nBody\n\n## Section\n\nMore\n"
    assert any(change.rule == "heading_blank_before" for change in report.changes)
    assert any(change.rule == "heading_blank_after" for change in report.changes)


def test_repeated_blank_line_reduction() -> None:
    source = "First paragraph\n\n\n\nSecond paragraph\n"
    output, report = normalize(source)

    assert output == "First paragraph\n\nSecond paragraph\n"
    assert any(change.rule == "blank_line_collapse" for change in report.changes)


def test_output_final_newline() -> None:
    source = "Single paragraph"
    output, _report = normalize(source)

    assert output.endswith("\n")
    assert not output.endswith("\n\n")


def test_idempotency() -> None:
    source = "Intro  \n* item\n3. step\n\n\n# Title\nBody\n```\nkeep  \n```\n"
    first_output, _ = normalize(source)
    second_output, second_report = normalize(first_output)

    assert second_output == first_output
    assert second_report.changes == []
