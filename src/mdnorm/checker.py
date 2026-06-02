# ============================================================
# FILE:          checker.py
# PROJECT:       MD Normalizer
# BRIEF:         Implements the advisory document-quality check rules (MDQ001-MDQ009).
# DOCUMENT:      docs/tool_framework.md; README.md; docs/decisions/DECISIONS.md
# REQUIREMENTS:  support-only; no formal requirement IDs assigned for v0.2.0
# COPYRIGHT:     Copyright (c) 2026 BelTech Systems LLC.
# LICENSE:       MIT License; see LICENSE in repository root.
# CLASSIFICATION: OPEN-SOURCE
# STANDARD:      Python 3.11+
# FUNCTIONS:
#   check(text, input_path, strict)
#     Runs all document-quality rules and returns a CheckReport.
#   format_check_finding(finding)
#     Formats a CheckFinding for human-readable console output.
# DEPENDENCIES:
#   Standard library: pathlib, re
#   Third-party:      none
#   Internal:         mdnorm.models, mdnorm.parser
# PORTABILITY:    Supports Python 3.11 or later on Windows, Linux, and macOS.
# IMPL. STATUS:   IN_REVIEW
# HISTORY:
#   2026-06-02  Cursor    [FEAT] Created with MDQ001-MDQ009 advisory check rules for v0.2.0
#   2026-06-02  Cursor    [FIX]  Updated _has_fence_language() to handle both ``` and ~~~ fences
#   2026-06-02  Cursor    [FIX]  MDQ003: use hierarchy-aware scope to avoid false positives on repeated subsection names (e.g. changelog)
#   2026-06-02  Cursor    [FIX]  MDQ004: do not fire when the next heading is a child (deeper level) of the current heading
# ============================================================

"""Advisory document-quality checker for MD Normalizer.

Implements rules MDQ001 through MDQ009, which surface engineering-document
hygiene issues without modifying the input file.

Tilde-fence note:
    The project parser (``mdnorm.parser``) recognises only backtick fences
    (`` ``` ``).  Tilde fences (``~~~``) are classified as ``PARAGRAPH`` blocks
    and are therefore invisible to ``_check_fence_language_tags`` (MDQ006) and
    to the fence-exclusion logic used by MDQ005/MDQ008/MDQ009.  The helper
    ``_has_fence_language()`` is written to strip both fence character types so
    the function remains correct if the parser is extended to support tilde
    fences in a future version.

The file header above is the authoritative engineering metadata source for
this module.
"""

from __future__ import annotations

import re
from pathlib import Path

from mdnorm import __version__
from mdnorm.models import Block, BlockType, CheckFinding, CheckReport
from mdnorm.parser import parse

# Regex patterns used by multiple rules.
_TODO_FIXME_RE = re.compile(r"(?:TODO|FIXME)", re.IGNORECASE)
_MARKDOWN_LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]*)\)")
_EXTERNAL_LINK_PREFIXES = ("http://", "https://", "mailto:", "#")


def check(
    text: str,
    input_path: str | Path | None = None,
    strict: bool = False,
) -> CheckReport:
    """Run all document-quality rules and return a CheckReport.

    Parameters
    ----------
    text:
        Raw text content of the Markdown or plain-text file.
    input_path:
        Path to the input file.  Required for MDQ007 (broken local link
        checking); if None the MDQ007 rule is silently skipped.
    strict:
        When True, warning-level findings make ``report.ok`` return False.
    """
    resolved_path = Path(input_path) if input_path is not None else None
    base_dir = resolved_path.parent if resolved_path is not None else None

    document = parse(text)
    blocks = document.blocks
    in_fence = _compute_fence_flags(blocks)

    report = CheckReport(
        tool="MD Normalizer",
        tool_version=__version__,
        input_path=str(resolved_path) if resolved_path is not None else None,
        strict=strict,
    )

    _check_h1_presence(blocks, report.findings)
    _check_duplicate_headings(blocks, report.findings)
    _check_empty_sections(blocks, report.findings)
    _check_todo_fixme(blocks, in_fence, report.findings)
    _check_fence_language_tags(blocks, report.findings)
    _check_broken_local_links(blocks, in_fence, base_dir, report.findings)
    _check_excessive_blank_lines(blocks, in_fence, report.findings)
    _check_trailing_whitespace(blocks, in_fence, report.findings)

    return report


def format_check_finding(finding: CheckFinding) -> str:
    """Format a CheckFinding as a human-readable console line.

    Examples
    --------
    ``warning MDQ001: Missing top-level H1 heading.``
    ``info MDQ005: line 42: TODO marker present.``
    """
    level = finding.level.lower()
    location = f" line {finding.line_number}:" if finding.line_number is not None else ""
    return f"{level} {finding.rule_id}:{location} {finding.message}"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _compute_fence_flags(blocks: list[Block]) -> list[bool]:
    """Return a per-block flag that is True when the block is inside (or is
    part of) a fenced code region.

    Both the opening ``` line and the closing ``` line are marked True so
    that trailing-whitespace and other checks naturally skip them.

    Note: The parser classifies completely blank lines inside fences as
    ``BlockType.BLANK`` rather than ``CODE_LINE`` because the blank-line
    check runs before the fence-state check.  This helper compensates by
    tracking fence state independently.
    """
    result: list[bool] = []
    in_fence = False
    for block in blocks:
        if block.block_type == BlockType.FENCED_CODE_START:
            result.append(True)
            in_fence = True
        elif block.block_type == BlockType.FENCED_CODE_END:
            result.append(True)
            in_fence = False
        else:
            result.append(in_fence)
    return result


def _normalize_heading_text(raw: str) -> str:
    """Strip # markers and normalise whitespace/case for comparison."""
    return " ".join(raw.lstrip("#").split()).lower()


def _heading_display_text(raw: str) -> str:
    """Strip # markers but preserve original casing for display."""
    return raw.lstrip("#").strip()


# ---------------------------------------------------------------------------
# MDQ001 – Missing top-level H1
# MDQ002 – Multiple top-level H1 headings
# Both rules inspect the same H1 list; combined for a single pass.
# ---------------------------------------------------------------------------

def _check_h1_presence(blocks: list[Block], findings: list[CheckFinding]) -> None:
    h1_blocks = [b for b in blocks if b.block_type == BlockType.HEADING and b.heading_level == 1]

    if not h1_blocks:
        findings.append(CheckFinding(
            rule_id="MDQ001",
            level="WARNING",
            message="Missing top-level H1 heading.",
            details="Most engineering documents should have a clear document title as an H1 heading.",
        ))
    elif len(h1_blocks) > 1:
        findings.append(CheckFinding(
            rule_id="MDQ002",
            level="WARNING",
            message=f"Multiple top-level H1 headings ({len(h1_blocks)} found).",
            line_number=h1_blocks[1].line_number,
            details="Multiple H1 headings often indicate unclear document structure.",
        ))


# ---------------------------------------------------------------------------
# MDQ003 – Duplicate heading text
# ---------------------------------------------------------------------------

def _check_duplicate_headings(blocks: list[Block], findings: list[CheckFinding]) -> None:
    """Flag headings whose normalised text duplicates a sibling within the same
    parent-heading scope.

    Scope is tracked via an ancestor stack: two headings are siblings (and
    therefore comparable for duplicates) only when they share the same sequence
    of ancestor headings.  This prevents false positives in structured documents
    such as changelogs, where subsection names like "Added" legitimately repeat
    under different version headings.

    Example that should NOT trigger MDQ003::

        ## v2.0
        ### Added   ← scope: ("v2.0",)
        ## v1.0
        ### Added   ← scope: ("v1.0",) – different parent, not a duplicate
    """
    # Maps scope_key → {normalised_text: first_line_number}
    seen_by_scope: dict[tuple[str, ...], dict[str, int]] = {}
    # Stack of (level, normalised_text) for the current ancestor chain.
    ancestor_stack: list[tuple[int, str]] = []

    for block in blocks:
        if block.block_type != BlockType.HEADING:
            continue

        level = block.heading_level
        normalized = _normalize_heading_text(block.text)

        # Pop ancestors at the same or deeper level to expose the parent scope.
        while ancestor_stack and ancestor_stack[-1][0] >= level:
            ancestor_stack.pop()

        scope_key = tuple(a[1] for a in ancestor_stack)
        scope_seen = seen_by_scope.setdefault(scope_key, {})

        if normalized in scope_seen:
            display = _heading_display_text(block.text)
            findings.append(CheckFinding(
                rule_id="MDQ003",
                level="WARNING",
                message=f"Duplicate heading text: '{display}'.",
                line_number=block.line_number,
                details=f"Heading text matches heading at line {scope_seen[normalized]}.",
            ))
        else:
            scope_seen[normalized] = block.line_number

        # Push current heading so its children inherit it as a scope ancestor.
        ancestor_stack.append((level, normalized))


# ---------------------------------------------------------------------------
# MDQ004 – Empty section
# ---------------------------------------------------------------------------

def _check_empty_sections(blocks: list[Block], findings: list[CheckFinding]) -> None:
    """Flag headings that have no meaningful content in their body.

    A section is considered empty when the first non-blank block that follows it
    is either absent (end of file) or a heading at the **same or higher** level
    (same or lower level number).

    A section is **not** considered empty when the next meaningful block is a
    child heading (higher level number / deeper nesting), because a heading
    followed immediately by subsection headings is valid document structure.

    Example that should NOT trigger MDQ004::

        # Document Title   ← level 1, followed by level 2 child → not empty
        ## First Section
        Content here.

    Example that SHOULD trigger MDQ004::

        ## Empty Section   ← level 2, followed by another level-2 → empty
        ## Next Section
    """
    for i, block in enumerate(blocks):
        if block.block_type != BlockType.HEADING:
            continue
        # Scan forward for the first non-blank block after this heading.
        next_meaningful = None
        for j in range(i + 1, len(blocks)):
            if blocks[j].block_type != BlockType.BLANK:
                next_meaningful = blocks[j]
                break

        if next_meaningful is None:
            # Heading at end of file with no content at all.
            findings.append(CheckFinding(
                rule_id="MDQ004",
                level="INFO",
                message=f"Empty section: '{_heading_display_text(block.text)}'.",
                line_number=block.line_number,
                details="Section has no meaningful content before end of file.",
            ))
        elif next_meaningful.block_type == BlockType.HEADING:
            next_level = next_meaningful.heading_level
            if next_level <= block.heading_level:
                # Same level (sibling) or higher level (parent) follows with no
                # content — this heading's body is empty.
                findings.append(CheckFinding(
                    rule_id="MDQ004",
                    level="INFO",
                    message=f"Empty section: '{_heading_display_text(block.text)}'.",
                    line_number=block.line_number,
                    details="Section has no meaningful content before the next heading.",
                ))
            # else: next heading is a child (deeper level) → section is not empty.


# ---------------------------------------------------------------------------
# MDQ005 – TODO or FIXME marker outside code block
# ---------------------------------------------------------------------------

def _check_todo_fixme(
    blocks: list[Block],
    in_fence: list[bool],
    findings: list[CheckFinding],
) -> None:
    for i, block in enumerate(blocks):
        if in_fence[i]:
            continue
        if _TODO_FIXME_RE.search(block.text):
            match = _TODO_FIXME_RE.search(block.text)
            marker = match.group(0).upper() if match else "TODO/FIXME"
            findings.append(CheckFinding(
                rule_id="MDQ005",
                level="INFO",
                message=f"{marker} marker present.",
                line_number=block.line_number,
                details=f"{marker} found outside fenced code block.",
            ))


# ---------------------------------------------------------------------------
# MDQ006 – Fenced code block missing language tag
# ---------------------------------------------------------------------------

def _check_fence_language_tags(blocks: list[Block], findings: list[CheckFinding]) -> None:
    for block in blocks:
        if block.block_type != BlockType.FENCED_CODE_START:
            continue
        if not _has_fence_language(block.text):
            findings.append(CheckFinding(
                rule_id="MDQ006",
                level="INFO",
                message="Fenced code block missing language tag.",
                line_number=block.line_number,
                details="Add a language identifier after the opening fence, e.g. ```python.",
            ))


_FENCE_CHARS_RE = re.compile(r"^[`~]+")


def _has_fence_language(fence_line: str) -> bool:
    """Return True if the fence opening line includes a non-empty language tag.

    Strips both backtick (`` ` ``) and tilde (``~``) fence characters from the
    start of the line so the function is correct for both fence styles.  Note
    that the current parser only emits ``FENCED_CODE_START`` for backtick
    fences; tilde fences fall through to ``PARAGRAPH`` and never reach this
    function.  The tilde handling is defensive for future parser extensions.
    """
    stripped = fence_line.strip()
    after_fence = _FENCE_CHARS_RE.sub("", stripped)
    return bool(after_fence.strip())


# ---------------------------------------------------------------------------
# MDQ007 – Broken local Markdown link
# ---------------------------------------------------------------------------

def _check_broken_local_links(
    blocks: list[Block],
    in_fence: list[bool],
    base_dir: Path | None,
    findings: list[CheckFinding],
) -> None:
    if base_dir is None:
        return

    for i, block in enumerate(blocks):
        if in_fence[i]:
            continue
        for match in _MARKDOWN_LINK_RE.finditer(block.text):
            target = match.group(2).strip()
            if any(target.startswith(p) for p in _EXTERNAL_LINK_PREFIXES):
                continue
            # Strip anchor fragment; keep only the path part.
            path_part = target.split("#")[0].strip()
            if not path_part:
                continue  # anchor-only link
            resolved = base_dir / path_part
            if not resolved.exists():
                findings.append(CheckFinding(
                    rule_id="MDQ007",
                    level="WARNING",
                    message=f"Broken local link target: {path_part}",
                    line_number=block.line_number,
                    details=f"Link target '{path_part}' does not exist relative to the input file.",
                ))


# ---------------------------------------------------------------------------
# MDQ008 – Excessive consecutive blank lines outside code block
# ---------------------------------------------------------------------------

def _check_excessive_blank_lines(
    blocks: list[Block],
    in_fence: list[bool],
    findings: list[CheckFinding],
) -> None:
    blank_run_start: int | None = None
    blank_count = 0

    def _flush() -> None:
        nonlocal blank_count, blank_run_start
        if blank_count > 2 and blank_run_start is not None:
            findings.append(CheckFinding(
                rule_id="MDQ008",
                level="INFO",
                message=f"Excessive consecutive blank lines ({blank_count}).",
                line_number=blank_run_start,
                details=f"{blank_count} consecutive blank lines found; more than 2 is excessive.",
            ))
        blank_count = 0
        blank_run_start = None

    for i, block in enumerate(blocks):
        if in_fence[i]:
            _flush()
            continue
        if block.block_type == BlockType.BLANK:
            if blank_run_start is None:
                blank_run_start = block.line_number
            blank_count += 1
        else:
            _flush()

    _flush()


# ---------------------------------------------------------------------------
# MDQ009 – Trailing whitespace outside code block
# ---------------------------------------------------------------------------

def _check_trailing_whitespace(
    blocks: list[Block],
    in_fence: list[bool],
    findings: list[CheckFinding],
) -> None:
    for i, block in enumerate(blocks):
        if in_fence[i]:
            continue
        if block.text != block.text.rstrip():
            findings.append(CheckFinding(
                rule_id="MDQ009",
                level="INFO",
                message="Trailing whitespace outside code block.",
                line_number=block.line_number,
                details="Line has trailing whitespace characters.",
            ))
