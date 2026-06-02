"""Fixture-based regression tests for the mdnorm.checker module.

Tests in this file load small Markdown documents from
tests/fixtures/release_docs/ and verify checker behaviour on realistic
engineering-document structures.  They complement the synthetic unit tests in
test_checker.py by ensuring the rules behave correctly on documents that
resemble real-world README, CHANGELOG, and DECISIONS files.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from mdnorm.checker import check
from mdnorm.models import BlockType, CheckFinding
from mdnorm.parser import parse

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

FIXTURES_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "release_docs"


def _rule_ids(findings: list[CheckFinding]) -> list[str]:
    return [f.rule_id for f in findings]


# ---------------------------------------------------------------------------
# README-like fixture
# ---------------------------------------------------------------------------


def test_readme_like_fixture_has_no_findings() -> None:
    """A clean README-like document produces no check findings."""
    fixture = FIXTURES_DIR / "readme_like.md"
    report = check(fixture.read_text(encoding="utf-8"), input_path=fixture)
    assert report.findings == [], (
        f"Expected no findings; got: {[str(f) for f in report.findings]}"
    )


# ---------------------------------------------------------------------------
# CHANGELOG-like fixture — MDQ003 hierarchy-awareness
# ---------------------------------------------------------------------------


def test_changelog_like_fixture_has_no_findings() -> None:
    """A clean CHANGELOG-like document produces no check findings."""
    fixture = FIXTURES_DIR / "changelog_like.md"
    report = check(fixture.read_text(encoding="utf-8"), input_path=fixture)
    assert report.findings == [], (
        f"Expected no findings; got: {[str(f) for f in report.findings]}"
    )


def test_changelog_like_fixture_no_mdq003_false_positive() -> None:
    """Repeated subsection names under different parent versions do not trigger MDQ003."""
    fixture = FIXTURES_DIR / "changelog_like.md"
    report = check(fixture.read_text(encoding="utf-8"), input_path=fixture)
    assert "MDQ003" not in _rule_ids(report.findings)


def test_changelog_like_fixture_no_mdq004_false_positive() -> None:
    """Version headings followed by sub-sections are not reported as empty (MDQ004)."""
    fixture = FIXTURES_DIR / "changelog_like.md"
    report = check(fixture.read_text(encoding="utf-8"), input_path=fixture)
    assert "MDQ004" not in _rule_ids(report.findings)


# ---------------------------------------------------------------------------
# DECISIONS-like fixture — MDQ004 parent/child heading
# ---------------------------------------------------------------------------


def test_decisions_like_fixture_has_no_findings() -> None:
    """A clean DECISIONS-like document produces no check findings."""
    fixture = FIXTURES_DIR / "decisions_like.md"
    report = check(fixture.read_text(encoding="utf-8"), input_path=fixture)
    assert report.findings == [], (
        f"Expected no findings; got: {[str(f) for f in report.findings]}"
    )


def test_decisions_like_fixture_no_mdq004_on_title() -> None:
    """The top-level H1 title followed immediately by an H2 does not trigger MDQ004."""
    fixture = FIXTURES_DIR / "decisions_like.md"
    report = check(fixture.read_text(encoding="utf-8"), input_path=fixture)
    assert "MDQ004" not in _rule_ids(report.findings)


# ---------------------------------------------------------------------------
# Code blocks fixture — rules exclude fenced content
# ---------------------------------------------------------------------------


def test_code_blocks_fixture_has_no_findings() -> None:
    """TODO, trailing whitespace, and excessive blank lines inside fences do not fire."""
    fixture = FIXTURES_DIR / "code_blocks.md"
    report = check(fixture.read_text(encoding="utf-8"), input_path=fixture)
    assert report.findings == [], (
        f"Expected no findings; got: {[str(f) for f in report.findings]}"
    )


def test_code_blocks_fixture_todo_inside_fence_not_flagged() -> None:
    """MDQ005 does not fire for a TODO marker that appears inside a fenced code block."""
    fixture = FIXTURES_DIR / "code_blocks.md"
    report = check(fixture.read_text(encoding="utf-8"), input_path=fixture)
    assert "MDQ005" not in _rule_ids(report.findings)


def test_code_blocks_fixture_trailing_ws_inside_fence_not_flagged() -> None:
    """MDQ009 does not fire for trailing whitespace that appears inside a fenced code block."""
    fixture = FIXTURES_DIR / "code_blocks.md"
    report = check(fixture.read_text(encoding="utf-8"), input_path=fixture)
    assert "MDQ009" not in _rule_ids(report.findings)


def test_code_blocks_fixture_excessive_blanks_inside_fence_not_flagged() -> None:
    """MDQ008 does not fire for excessive blank lines that appear inside a fenced code block."""
    fixture = FIXTURES_DIR / "code_blocks.md"
    report = check(fixture.read_text(encoding="utf-8"), input_path=fixture)
    assert "MDQ008" not in _rule_ids(report.findings)


# ---------------------------------------------------------------------------
# Nested examples fixture
# ---------------------------------------------------------------------------


def test_nested_examples_fixture_has_no_findings() -> None:
    """The nested examples fixture uses the correct separate-block pattern and passes check."""
    fixture = FIXTURES_DIR / "nested_examples.md"
    report = check(fixture.read_text(encoding="utf-8"), input_path=fixture)
    assert report.findings == [], (
        f"Expected no findings; got: {[str(f) for f in report.findings]}"
    )


# ---------------------------------------------------------------------------
# Tilde fence fixture — known limitation documentation
# ---------------------------------------------------------------------------


def test_tilde_fence_fixture_has_no_findings() -> None:
    """The tilde fence fixture document is clean (no violations in its content)."""
    fixture = FIXTURES_DIR / "tilde_fences.md"
    report = check(fixture.read_text(encoding="utf-8"), input_path=fixture)
    assert report.findings == [], (
        f"Expected no findings; got: {[str(f) for f in report.findings]}"
    )


def test_tilde_fence_lines_parsed_as_paragraphs() -> None:
    """The parser classifies ~~~ lines as PARAGRAPH, not FENCED_CODE_START."""
    fixture = FIXTURES_DIR / "tilde_fences.md"
    doc = parse(fixture.read_text(encoding="utf-8"))
    tilde_blocks = [b for b in doc.blocks if b.text.startswith("~~~")]
    assert tilde_blocks, "Expected at least one tilde line in the fixture"
    for block in tilde_blocks:
        assert block.block_type == BlockType.PARAGRAPH, (
            f"Line {block.line_number}: expected PARAGRAPH, got {block.block_type}"
        )


def test_tilde_fence_limitation_content_is_not_excluded() -> None:
    """Known limitation: a TODO inside a tilde fence IS reported by MDQ005.

    The parser does not recognise ~~~ as a fence marker, so tilde-fenced
    content is not excluded from check rules.  This test documents that
    behaviour explicitly so the limitation is visible in the test suite.
    """
    source = "# Title\n\n~~~python\n# TODO: annotation inside tilde fence\n~~~\n"
    report = check(source)
    assert any(f.rule_id == "MDQ005" for f in report.findings), (
        "Expected MDQ005 to fire for TODO inside tilde fence (parser does not "
        "recognise ~~~ as a code fence — known limitation)"
    )


# ---------------------------------------------------------------------------
# Broken / valid local link fixture — MDQ007
# ---------------------------------------------------------------------------


def test_broken_link_fixture_detects_missing_file() -> None:
    """MDQ007 fires for a link that points to a file that does not exist."""
    fixture = FIXTURES_DIR / "has_broken_link.md"
    report = check(fixture.read_text(encoding="utf-8"), input_path=fixture)
    assert "MDQ007" in _rule_ids(report.findings), (
        "Expected MDQ007 for the broken link in has_broken_link.md"
    )


def test_broken_link_fixture_broken_link_message_names_target() -> None:
    """The MDQ007 finding message identifies the missing link target."""
    fixture = FIXTURES_DIR / "has_broken_link.md"
    report = check(fixture.read_text(encoding="utf-8"), input_path=fixture)
    mdq007_messages = [f.message for f in report.findings if f.rule_id == "MDQ007"]
    assert any("nonexistent_setup_guide" in m for m in mdq007_messages), (
        f"Expected the broken link target name in finding message; got: {mdq007_messages}"
    )


def test_broken_link_fixture_valid_link_not_flagged() -> None:
    """MDQ007 does not fire for the link to readme_like.md, which exists."""
    fixture = FIXTURES_DIR / "has_broken_link.md"
    report = check(fixture.read_text(encoding="utf-8"), input_path=fixture)
    mdq007_messages = [f.message for f in report.findings if f.rule_id == "MDQ007"]
    # The valid link "readme_like.md" must not appear in any MDQ007 message.
    assert not any("readme_like.md" in m for m in mdq007_messages), (
        f"readme_like.md should not be flagged as broken; MDQ007 messages: {mdq007_messages}"
    )
