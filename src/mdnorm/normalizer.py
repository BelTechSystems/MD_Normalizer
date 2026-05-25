# ============================================================
# FILE:          normalizer.py
# PROJECT:       MD Normalizer
# BRIEF:         Applies deterministic Markdown normalization rules and records changes.
# DOCUMENT:      docs/tool_framework.md; README.md
# REQUIREMENTS:  support-only; no formal requirement IDs assigned for v0.1.0
# COPYRIGHT:     Copyright (c) 2026 BelTech Systems LLC.
# LICENSE:       MIT License; see LICENSE in repository root.
# CLASSIFICATION: OPEN-SOURCE
# STANDARD:      Python 3.11+
# FUNCTIONS:
#   normalize(text, report)
#     Applies deterministic normalization and returns output with a change report.
# DEPENDENCIES:
#   Standard library: re
#   Third-party:      none
#   Internal:         mdnorm.models, mdnorm.parser
# PORTABILITY:    Supports Python 3.11 or later on Windows, Linux, and macOS.
# IMPL. STATUS:   IN_REVIEW
# HISTORY:
#   2026-05-25  Cursor    [DOCS] Replaced minimal SPDX header with STD-006 style metadata header
# ============================================================

"""Deterministic Markdown normalization rules.

The file header above is the authoritative engineering metadata source for
this module.
"""

from __future__ import annotations

import re

from mdnorm.models import (
    Block,
    BlockType,
    NormalizationChange,
    NormalizationReport,
)
from mdnorm.parser import parse

_UNORDERED_MARKER_RE = re.compile(r"^(\s*)[-*+]+(\s+)(.*)$")
_ORDERED_MARKER_RE = re.compile(r"^(\s*)\d+[.)](\s+)(.*)$")
_CODE_BLOCK_TYPES = {
    BlockType.FENCED_CODE_START,
    BlockType.FENCED_CODE_END,
    BlockType.CODE_LINE,
}


def normalize(text: str, report: NormalizationReport | None = None) -> tuple[str, NormalizationReport]:
    """Normalize Markdown text and return the result with a change report."""
    document = parse(text)
    active_report = report or NormalizationReport()

    blocks = [_normalize_block_content(block, active_report) for block in document.blocks]
    blocks = _normalize_ordered_list_groups(blocks, active_report)
    lines = _apply_blank_line_rules(blocks, active_report)
    output = _finalize_output(lines)

    return output, active_report


def _normalize_block_content(block: Block, report: NormalizationReport) -> Block:
    if block.block_type in _CODE_BLOCK_TYPES:
        return block

    if block.block_type == BlockType.BLANK:
        return _apply_change(block, "", report, "blank_line", "Normalize blank line")

    updated = block.text

    stripped = updated.rstrip()
    if stripped != updated:
        updated = stripped
        _record_change(
            report,
            block,
            "trailing_whitespace",
            "Remove trailing whitespace",
            block.text,
            updated,
        )

    if block.block_type == BlockType.UNORDERED_LIST_ITEM:
        normalized = _normalize_unordered_marker(updated)
        if normalized != updated:
            _record_change(
                report,
                block,
                "unordered_list_marker",
                "Normalize unordered list marker to '-'",
                updated,
                normalized,
            )
            updated = normalized

    if updated != block.text:
        return Block(
            line_number=block.line_number,
            text=updated,
            block_type=block.block_type,
            heading_level=block.heading_level,
        )

    return block


def _normalize_unordered_marker(line: str) -> str:
    match = _UNORDERED_MARKER_RE.match(line)
    if not match:
        return line

    indent, spacing, content = match.groups()
    return f"{indent}-{spacing}{content}"


def _normalize_ordered_list_groups(
    blocks: list[Block],
    report: NormalizationReport,
) -> list[Block]:
    normalized_blocks = list(blocks)
    index = 0

    while index < len(normalized_blocks):
        block = normalized_blocks[index]
        if block.block_type != BlockType.ORDERED_LIST_ITEM:
            index += 1
            continue

        start = index
        while (
            index < len(normalized_blocks)
            and normalized_blocks[index].block_type == BlockType.ORDERED_LIST_ITEM
        ):
            index += 1

        number = 1
        for item_index in range(start, index):
            item = normalized_blocks[item_index]
            updated = _normalize_ordered_marker(item.text, number)
            if updated != item.text:
                _record_change(
                    report,
                    item,
                    "ordered_list_number",
                    "Renumber ordered list item",
                    item.text,
                    updated,
                )
                normalized_blocks[item_index] = Block(
                    line_number=item.line_number,
                    text=updated,
                    block_type=item.block_type,
                    heading_level=item.heading_level,
                )
            number += 1

    return normalized_blocks


def _normalize_ordered_marker(line: str, number: int) -> str:
    match = _ORDERED_MARKER_RE.match(line)
    if not match:
        return line

    indent, spacing, content = match.groups()
    return f"{indent}{number}.{spacing}{content}"


def _apply_blank_line_rules(
    blocks: list[Block],
    report: NormalizationReport,
) -> list[str]:
    collapsed = _collapse_blank_blocks(blocks, report)
    spaced = _normalize_heading_spacing(collapsed, report)
    return [block.text for block in spaced]


def _collapse_blank_blocks(
    blocks: list[Block],
    report: NormalizationReport,
) -> list[Block]:
    if not blocks:
        return []

    collapsed: list[Block] = []
    blank_run = 0

    for block in blocks:
        if block.block_type == BlockType.BLANK:
            blank_run += 1
            continue

        if blank_run:
            collapsed.append(
                _blank_block_after(collapsed[-1].line_number if collapsed else 0)
            )
            if blank_run > 1:
                _record_change(
                    report,
                    block,
                    "blank_line_collapse",
                    "Collapse repeated blank lines",
                    "\n" * blank_run,
                    "",
                )
            blank_run = 0

        collapsed.append(block)

    if blank_run:
        collapsed.append(
            _blank_block_after(collapsed[-1].line_number if collapsed else 0)
        )
        if blank_run > 1 and collapsed:
            _record_change(
                report,
                collapsed[-1],
                "blank_line_collapse",
                "Collapse repeated blank lines",
                "\n" * blank_run,
                "",
            )

    return collapsed


def _normalize_heading_spacing(
    blocks: list[Block],
    report: NormalizationReport,
) -> list[Block]:
    if not blocks:
        return []

    spaced: list[Block] = []
    index = 0

    while index < len(blocks):
        block = blocks[index]

        if block.block_type == BlockType.HEADING:
            if index > 0 and spaced and spaced[-1].block_type != BlockType.BLANK:
                previous = spaced[-1]
                blank = _blank_block_after(previous.line_number)
                spaced.append(blank)
                _record_change(
                    report,
                    block,
                    "heading_blank_before",
                    "Insert blank line before heading",
                    previous.text,
                    f"{previous.text}\n",
                )

            spaced.append(block)

            next_block = blocks[index + 1] if index + 1 < len(blocks) else None
            if next_block is not None and next_block.block_type != BlockType.BLANK:
                blank = _blank_block_after(block.line_number)
                spaced.append(blank)
                _record_change(
                    report,
                    block,
                    "heading_blank_after",
                    "Insert blank line after heading",
                    f"{block.text}\n{next_block.text}",
                    f"{block.text}\n\n{next_block.text}",
                )
            index += 1
            continue

        spaced.append(block)
        index += 1

    return spaced


def _blank_block_after(line_number: int) -> Block:
    return Block(
        line_number=line_number,
        text="",
        block_type=BlockType.BLANK,
    )


def _finalize_output(lines: list[str]) -> str:
    trimmed = list(lines)
    while trimmed and trimmed[-1] == "":
        trimmed.pop()

    if not trimmed:
        return "\n"

    return "\n".join(trimmed) + "\n"


def _apply_change(
    block: Block,
    updated: str,
    report: NormalizationReport,
    rule: str,
    description: str,
) -> Block:
    if updated != block.text:
        _record_change(report, block, rule, description, block.text, updated)

    return Block(
        line_number=block.line_number,
        text=updated,
        block_type=block.block_type,
        heading_level=block.heading_level,
    )


def _record_change(
    report: NormalizationReport,
    block: Block,
    rule: str,
    description: str,
    before: str,
    after: str,
) -> None:
    if before == after:
        return

    report.changes.append(
        NormalizationChange(
            line_number=block.line_number,
            rule=rule,
            description=description,
            before=before,
            after=after,
        )
    )
