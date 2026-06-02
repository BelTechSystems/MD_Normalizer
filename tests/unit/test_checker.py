"""Unit tests for the mdnorm.checker module (MDQ001-MDQ009)."""

from __future__ import annotations

from pathlib import Path

import pytest

from mdnorm.checker import check, format_check_finding
from mdnorm.models import CheckFinding


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _rule_ids(report_findings: list[CheckFinding]) -> list[str]:
    return [f.rule_id for f in report_findings]


# ---------------------------------------------------------------------------
# MDQ001 – Missing top-level H1
# ---------------------------------------------------------------------------

def test_mdq001_fires_when_no_h1_heading() -> None:
    source = "## Intro\n\nSome text.\n"
    report = check(source)
    assert "MDQ001" in _rule_ids(report.findings)


def test_mdq001_fires_for_no_headings_at_all() -> None:
    source = "Just a paragraph with no headings.\n"
    report = check(source)
    assert "MDQ001" in _rule_ids(report.findings)


def test_mdq001_does_not_fire_when_h1_present() -> None:
    source = "# Title\n\nContent.\n"
    report = check(source)
    assert "MDQ001" not in _rule_ids(report.findings)


# ---------------------------------------------------------------------------
# MDQ002 – Multiple top-level H1 headings
# ---------------------------------------------------------------------------

def test_mdq002_fires_when_multiple_h1() -> None:
    source = "# First\n\nText.\n\n# Second\n\nMore text.\n"
    report = check(source)
    assert "MDQ002" in _rule_ids(report.findings)


def test_mdq002_points_to_second_h1_line() -> None:
    source = "# First\n\nText.\n\n# Second\n\nMore text.\n"
    report = check(source)
    finding = next(f for f in report.findings if f.rule_id == "MDQ002")
    assert finding.line_number == 5  # "# Second" is line 5


def test_mdq002_does_not_fire_for_single_h1() -> None:
    source = "# Only Title\n\nContent.\n"
    report = check(source)
    assert "MDQ002" not in _rule_ids(report.findings)


# ---------------------------------------------------------------------------
# MDQ003 – Duplicate heading text
# ---------------------------------------------------------------------------

def test_mdq003_fires_for_duplicate_heading() -> None:
    source = "# Title\n\n## Intro\n\nText.\n\n## Intro\n\nMore text.\n"
    report = check(source)
    assert "MDQ003" in _rule_ids(report.findings)


def test_mdq003_comparison_is_case_insensitive() -> None:
    source = "# Title\n\n## Introduction\n\nText.\n\n## INTRODUCTION\n\nMore.\n"
    report = check(source)
    assert "MDQ003" in _rule_ids(report.findings)


def test_mdq003_does_not_fire_for_unique_headings() -> None:
    source = "# Title\n\nContent.\n\n## Section A\n\nText.\n\n## Section B\n\nMore.\n"
    report = check(source)
    assert "MDQ003" not in _rule_ids(report.findings)


def test_mdq003_does_not_fire_for_headings_under_different_parents() -> None:
    """Changelog pattern: same subsection names under different version headings.

    '### Added' and '### Notes' legitimately repeat under each release section.
    MDQ003 must not fire because the headings are in different parent scopes.
    """
    source = (
        "# Changelog\n\n"
        "## v2.0\n\n"
        "### Added\n\n- Feature X\n\n"
        "### Notes\n\nNotes for v2.\n\n"
        "## v1.0\n\n"
        "### Added\n\n- Feature Y\n\n"
        "### Notes\n\nNotes for v1.\n"
    )
    report = check(source)
    assert "MDQ003" not in _rule_ids(report.findings)


def test_mdq003_fires_for_duplicate_siblings_under_same_parent() -> None:
    """Two same-named headings under the same parent section should still fire."""
    source = (
        "# Doc\n\n"
        "## Section\n\n"
        "### Sub\n\nContent.\n\n"
        "### Sub\n\nMore content.\n"  # ← duplicate sibling under ## Section
    )
    report = check(source)
    assert "MDQ003" in _rule_ids(report.findings)


# ---------------------------------------------------------------------------
# MDQ004 – Empty section
# ---------------------------------------------------------------------------

def test_mdq004_fires_for_empty_section() -> None:
    source = "# Title\n\nContent.\n\n## Empty\n\n## Next\n\nText.\n"
    report = check(source)
    mdq004 = [f for f in report.findings if f.rule_id == "MDQ004"]
    # "## Empty" at line 5 has no content before "## Next"
    assert any(f.line_number == 5 for f in mdq004)


def test_mdq004_fires_for_heading_at_end_of_file() -> None:
    source = "# Title\n\nContent.\n\n## Trailing Heading\n"
    report = check(source)
    mdq004 = [f for f in report.findings if f.rule_id == "MDQ004"]
    assert len(mdq004) >= 1


def test_mdq004_does_not_fire_when_section_has_content() -> None:
    source = "# Title\n\nContent here.\n\n## Section\n\nMore content here.\n"
    report = check(source)
    assert "MDQ004" not in _rule_ids(report.findings)


def test_mdq004_does_not_fire_when_child_heading_follows() -> None:
    """Document title followed by a deeper-level heading is valid structure.

    '# Document Title' → '## First Section' should not trigger MDQ004 because
    '## First Section' is a child (deeper level) of the title.
    """
    source = "# Document Title\n\n## First Section\n\nContent.\n"
    report = check(source)
    assert "MDQ004" not in _rule_ids(report.findings)


def test_mdq004_does_not_fire_for_deeper_child_heading() -> None:
    """H2 immediately followed by H3 is also valid (H3 is a child of H2)."""
    source = "## Section\n\n### Subsection\n\nContent.\n"
    report = check(source)
    assert "MDQ004" not in _rule_ids(report.findings)


def test_mdq004_fires_when_parent_level_heading_follows() -> None:
    """H2 followed immediately by H1 with no content — the H2 section is empty."""
    source = "## Section\n\n# New Title\n\nContent.\n"
    report = check(source)
    assert any(f.rule_id == "MDQ004" for f in report.findings)


def test_mdq004_decisions_doc_pattern_does_not_trigger() -> None:
    """Top-level title followed only by H2 decision entries should not trigger."""
    source = (
        "# MD Normalizer Decisions\n\n"
        "## D-001: First Decision\n\n"
        "Content of the decision.\n\n"
        "## D-002: Second Decision\n\n"
        "Content of the second decision.\n"
    )
    report = check(source)
    assert "MDQ004" not in _rule_ids(report.findings)


def test_mdq004_changelog_pattern_does_not_trigger() -> None:
    """Version headings followed immediately by subsection headings should not fire."""
    source = (
        "# Changelog\n\n"
        "## v2.0\n\n"
        "### Added\n\n"
        "- Feature X\n"
    )
    report = check(source)
    assert "MDQ004" not in _rule_ids(report.findings)


# ---------------------------------------------------------------------------
# MDQ005 – TODO or FIXME marker outside code block
# ---------------------------------------------------------------------------

def test_mdq005_fires_for_todo_outside_code_block() -> None:
    source = "# Title\n\nTODO: fix this later.\n"
    report = check(source)
    assert "MDQ005" in _rule_ids(report.findings)


def test_mdq005_fires_for_fixme_outside_code_block() -> None:
    source = "# Title\n\nFIXME: this is broken.\n"
    report = check(source)
    assert "MDQ005" in _rule_ids(report.findings)


def test_mdq005_fires_case_insensitively() -> None:
    source = "# Title\n\ntodo: do something.\n"
    report = check(source)
    assert "MDQ005" in _rule_ids(report.findings)


def test_mdq005_does_not_fire_for_todo_inside_fenced_code_block() -> None:
    source = "# Title\n\n```python\n# TODO: fix this\n```\n"
    report = check(source)
    assert "MDQ005" not in _rule_ids(report.findings)


def test_mdq005_does_not_fire_for_fixme_inside_fenced_code_block() -> None:
    source = "# Title\n\n```python\n# FIXME: broken\n```\n"
    report = check(source)
    assert "MDQ005" not in _rule_ids(report.findings)


# ---------------------------------------------------------------------------
# MDQ006 – Fenced code block missing language tag
# ---------------------------------------------------------------------------

def test_mdq006_fires_for_fence_without_language_tag() -> None:
    source = "# Title\n\n```\ncode here\n```\n"
    report = check(source)
    assert "MDQ006" in _rule_ids(report.findings)


def test_mdq006_fires_for_fence_with_only_whitespace_after_ticks() -> None:
    source = "# Title\n\n```   \ncode here\n```\n"
    report = check(source)
    assert "MDQ006" in _rule_ids(report.findings)


def test_mdq006_does_not_fire_when_language_tag_present() -> None:
    source = "# Title\n\n```python\ncode here\n```\n"
    report = check(source)
    assert "MDQ006" not in _rule_ids(report.findings)


def test_mdq006_does_not_fire_for_text_language_tag() -> None:
    source = "# Title\n\n```text\nexample output\n```\n"
    report = check(source)
    assert "MDQ006" not in _rule_ids(report.findings)


def test_mdq006_tilde_fence_not_parsed_bare() -> None:
    """Bare tilde fences (~~~) are classified as PARAGRAPH by the parser.

    They are never seen as FENCED_CODE_START, so MDQ006 is not emitted.
    This test documents the current parser limitation: tilde fences are not
    recognised and therefore their language tag (or lack thereof) is invisible
    to the checker.
    """
    source = "# Title\n\n~~~\ncode here\n~~~\n"
    report = check(source)
    assert "MDQ006" not in _rule_ids(report.findings)


def test_mdq006_tilde_fence_not_parsed_with_language() -> None:
    """Tilde fences with a language tag are also not recognised by the parser.

    Same parser limitation: ~~~python is classified as PARAGRAPH, not as
    FENCED_CODE_START, so MDQ006 is not emitted.
    """
    source = "# Title\n\n~~~python\ncode here\n~~~\n"
    report = check(source)
    assert "MDQ006" not in _rule_ids(report.findings)


# ---------------------------------------------------------------------------
# MDQ007 – Broken local Markdown link
# ---------------------------------------------------------------------------

def test_mdq007_fires_for_nonexistent_local_file(tmp_path: Path) -> None:
    input_file = tmp_path / "doc.md"
    input_file.write_text(
        "# Title\n\nSee [missing file](nonexistent.md) for details.\n",
        encoding="utf-8",
    )
    report = check(input_file.read_text(encoding="utf-8"), input_path=input_file)
    assert "MDQ007" in _rule_ids(report.findings)


def test_mdq007_does_not_fire_for_existing_local_file(tmp_path: Path) -> None:
    target = tmp_path / "target.md"
    target.write_text("# Target\n", encoding="utf-8")
    input_file = tmp_path / "doc.md"
    input_file.write_text(
        "# Title\n\nSee [target](target.md) for details.\n",
        encoding="utf-8",
    )
    report = check(input_file.read_text(encoding="utf-8"), input_path=input_file)
    assert "MDQ007" not in _rule_ids(report.findings)


def test_mdq007_ignores_anchor_only_links() -> None:
    source = "# Title\n\nSee [section](#intro) for details.\n"
    report = check(source)
    assert "MDQ007" not in _rule_ids(report.findings)


def test_mdq007_ignores_https_links() -> None:
    source = "# Title\n\nSee [link](https://example.com) for details.\n"
    report = check(source)
    assert "MDQ007" not in _rule_ids(report.findings)


def test_mdq007_ignores_http_links() -> None:
    source = "# Title\n\nSee [link](http://example.com) for details.\n"
    report = check(source)
    assert "MDQ007" not in _rule_ids(report.findings)


def test_mdq007_ignores_mailto_links() -> None:
    source = "# Title\n\nEmail [us](mailto:info@example.com).\n"
    report = check(source)
    assert "MDQ007" not in _rule_ids(report.findings)


def test_mdq007_checks_path_only_when_link_has_anchor(tmp_path: Path) -> None:
    target = tmp_path / "setup.md"
    target.write_text("# Setup\n\n## Installation\n", encoding="utf-8")
    input_file = tmp_path / "doc.md"
    input_file.write_text(
        "# Title\n\nSee [setup](setup.md#installation).\n",
        encoding="utf-8",
    )
    report = check(input_file.read_text(encoding="utf-8"), input_path=input_file)
    assert "MDQ007" not in _rule_ids(report.findings)


def test_mdq007_skipped_when_no_input_path() -> None:
    source = "# Title\n\nSee [missing](nonexistent.md).\n"
    # Without input_path, MDQ007 cannot resolve relative links.
    report = check(source, input_path=None)
    assert "MDQ007" not in _rule_ids(report.findings)


# ---------------------------------------------------------------------------
# MDQ008 – Excessive consecutive blank lines outside code block
# ---------------------------------------------------------------------------

def test_mdq008_fires_for_three_consecutive_blank_lines() -> None:
    source = "First paragraph.\n\n\n\nSecond paragraph.\n"  # 3 blank lines
    report = check(source)
    assert "MDQ008" in _rule_ids(report.findings)


def test_mdq008_does_not_fire_for_two_blank_lines() -> None:
    source = "First paragraph.\n\n\nSecond paragraph.\n"  # 2 blank lines
    report = check(source)
    assert "MDQ008" not in _rule_ids(report.findings)


def test_mdq008_does_not_fire_for_blank_lines_inside_code_block() -> None:
    # 3 blank lines inside a fenced code block should not trigger MDQ008.
    source = "# Title\n\n```python\n\n\n\ncode\n```\n"
    report = check(source)
    assert "MDQ008" not in _rule_ids(report.findings)


# ---------------------------------------------------------------------------
# MDQ009 – Trailing whitespace outside code block
# ---------------------------------------------------------------------------

def test_mdq009_fires_for_trailing_whitespace_outside_code() -> None:
    source = "# Title\n\nParagraph with trailing spaces.   \n"
    report = check(source)
    assert "MDQ009" in _rule_ids(report.findings)


def test_mdq009_does_not_fire_for_trailing_whitespace_inside_code_block() -> None:
    source = "# Title\n\n```python\ncode with trailing spaces   \n```\n"
    report = check(source)
    assert "MDQ009" not in _rule_ids(report.findings)


def test_mdq009_does_not_fire_for_clean_lines() -> None:
    source = "# Title\n\nClean paragraph.\n"
    report = check(source)
    assert "MDQ009" not in _rule_ids(report.findings)


# ---------------------------------------------------------------------------
# Clean document – no findings
# ---------------------------------------------------------------------------

def test_no_findings_for_well_formed_document() -> None:
    source = (
        "# Title\n"
        "\n"
        "Introductory paragraph.\n"
        "\n"
        "## Section A\n"
        "\n"
        "Content under section A.\n"
        "\n"
        "## Section B\n"
        "\n"
        "Content under section B.\n"
        "\n"
        "```python\n"
        "print('hello')\n"
        "```\n"
    )
    report = check(source)
    assert report.findings == []


# ---------------------------------------------------------------------------
# format_check_finding
# ---------------------------------------------------------------------------

def test_format_finding_without_line_number() -> None:
    finding = CheckFinding(rule_id="MDQ001", level="WARNING", message="Missing top-level H1 heading.")
    assert format_check_finding(finding) == "warning MDQ001: Missing top-level H1 heading."


def test_format_finding_with_line_number() -> None:
    finding = CheckFinding(
        rule_id="MDQ005",
        level="INFO",
        message="TODO marker present.",
        line_number=42,
    )
    assert format_check_finding(finding) == "info MDQ005: line 42: TODO marker present."


# ---------------------------------------------------------------------------
# Report metadata
# ---------------------------------------------------------------------------

def test_check_report_contains_version() -> None:
    from mdnorm import __version__
    report = check("# Title\n\nContent.\n")
    assert report.tool_version == __version__


def test_check_report_strict_field_propagated() -> None:
    report = check("# Title\n\nContent.\n", strict=True)
    assert report.strict is True
