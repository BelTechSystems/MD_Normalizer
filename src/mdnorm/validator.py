# ============================================================
# FILE:          validator.py
# PROJECT:       MD Normalizer
# BRIEF:         Validates Markdown against baseline formatting and safety rules.
# DOCUMENT:      docs/tool_framework.md; README.md
# REQUIREMENTS:  support-only; no formal requirement IDs assigned for v0.1.0
# COPYRIGHT:     Copyright (c) 2026 BelTech Systems LLC.
# LICENSE:       MIT License; see LICENSE in repository root.
# CLASSIFICATION: OPEN-SOURCE
# STANDARD:      Python 3.11+
# FUNCTIONS/CLASSES:
#   validate(text)
#     Runs baseline Markdown validation checks.
#   format_message(message)
#     Formats a validation message for CLI output.
#   ValidationResult
#     Holds structured validation warnings and errors.
# DEPENDENCIES:
#   Standard library: re, dataclasses
#   Third-party:      none
#   Internal:         mdnorm.models, mdnorm.parser
# PORTABILITY:    Supports Python 3.11 or later on Windows, Linux, and macOS.
# IMPL. STATUS:   IN_REVIEW
# HISTORY:
#   2026-05-25  Cursor    [DOCS] Replaced minimal SPDX header with STD-006 style metadata header
#   2026-05-25  Cursor    [DOCS] Standardized FUNCTIONS/CLASSES label and section ordering
# ============================================================

"""Markdown validation checks.

The file header above is the authoritative engineering metadata source for
this module.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from mdnorm.models import BlockType, Document, ValidationMessage
from mdnorm.parser import parse

_HEADING_RE = re.compile(r"^(?P<level>#{1,6})\s+(?P<title>\S.*)$")
_MALFORMED_HEADING_RE = re.compile(r"^\s*#")
_CODE_BLOCK_TYPES = {
    BlockType.FENCED_CODE_START,
    BlockType.FENCED_CODE_END,
    BlockType.CODE_LINE,
}


@dataclass
class ValidationResult:
    """Structured validation outcome."""

    errors: list[ValidationMessage] = field(default_factory=list)
    warnings: list[ValidationMessage] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def validate(text: str) -> ValidationResult:
    """Validate Markdown text and return structured warnings and errors."""
    document = parse(text)
    result = ValidationResult()

    _check_empty_document(document, result)
    _check_unclosed_code_fence(document, result)
    _check_malformed_headings(document, result)
    _check_trailing_whitespace(document, result)
    _check_heading_jumps(document, result)

    return result


def format_message(message: ValidationMessage) -> str:
    """Format a validation message for CLI output."""
    location = (
        f"line {message.line_number}: "
        if message.line_number is not None
        else ""
    )
    return f"{message.level}: {location}{message.message}"


def _check_empty_document(document: Document, result: ValidationResult) -> None:
    has_content = any(
        block.block_type != BlockType.BLANK for block in document.blocks
    )
    if not has_content:
        result.errors.append(
            ValidationMessage(
                level="error",
                message="Document is empty.",
            )
        )


def _check_unclosed_code_fence(document: Document, result: ValidationResult) -> None:
    if not document.has_unclosed_code_fence:
        return

    fence_start_line = _unclosed_fence_start_line(document)
    result.errors.append(
        ValidationMessage(
            level="error",
            message="Unclosed fenced code block.",
            line_number=fence_start_line,
        )
    )


def _unclosed_fence_start_line(document: Document) -> int | None:
    in_fence = False
    start_line: int | None = None

    for block in document.blocks:
        if block.block_type == BlockType.FENCED_CODE_START:
            in_fence = True
            start_line = block.line_number
        elif block.block_type == BlockType.FENCED_CODE_END:
            in_fence = False
            start_line = None

    return start_line if in_fence else None


def _check_malformed_headings(document: Document, result: ValidationResult) -> None:
    for block in document.blocks:
        if block.block_type in _CODE_BLOCK_TYPES:
            continue

        if _is_malformed_heading(block.text):
            result.errors.append(
                ValidationMessage(
                    level="error",
                    message="Malformed heading.",
                    line_number=block.line_number,
                )
            )


def _is_malformed_heading(line: str) -> bool:
    if not _MALFORMED_HEADING_RE.match(line):
        return False

    return _HEADING_RE.match(line) is None


def _check_trailing_whitespace(document: Document, result: ValidationResult) -> None:
    for block in document.blocks:
        if block.block_type in _CODE_BLOCK_TYPES:
            continue

        if block.text != block.text.rstrip():
            result.errors.append(
                ValidationMessage(
                    level="error",
                    message="Trailing whitespace is not allowed.",
                    line_number=block.line_number,
                )
            )


def _check_heading_jumps(document: Document, result: ValidationResult) -> None:
    previous_level = 0

    for block in document.blocks:
        if block.block_type != BlockType.HEADING or block.heading_level is None:
            continue

        if previous_level and block.heading_level > previous_level + 1:
            result.warnings.append(
                ValidationMessage(
                    level="warning",
                    message=(
                        "Heading level jumps from "
                        f"{previous_level} to {block.heading_level}."
                    ),
                    line_number=block.line_number,
                )
            )

        previous_level = block.heading_level
