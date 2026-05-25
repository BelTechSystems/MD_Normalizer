# ============================================================
# FILE:          models.py
# PROJECT:       MD Normalizer
# BRIEF:         Defines shared dataclasses and enums for parsed and normalized documents.
# DOCUMENT:      docs/tool_framework.md; README.md
# REQUIREMENTS:  support-only; no formal requirement IDs assigned for v0.1.0
# COPYRIGHT:     Copyright (c) 2026 BelTech Systems LLC.
# LICENSE:       MIT License; see LICENSE in repository root.
# CLASSIFICATION: OPEN-SOURCE
# STANDARD:      Python 3.11+
# CLASSES:
#   BlockType, Block, Document
#     Parsed document line classification and structure.
#   ValidationMessage, NormalizationChange, NormalizationReport
#     Validation and normalization report data models.
# DEPENDENCIES:
#   Standard library: dataclasses, enum
#   Third-party:      none
#   Internal:         none
# PORTABILITY:    Supports Python 3.11 or later on Windows, Linux, and macOS.
# IMPL. STATUS:   IN_REVIEW
# HISTORY:
#   2026-05-25  Cursor    [DOCS] Replaced minimal SPDX header with STD-006 style metadata header
# ============================================================

"""Shared data models for parsed and normalized documents.

The file header above is the authoritative engineering metadata source for
this module.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class BlockType(str, Enum):
    """Line classification for the baseline parser."""

    HEADING = "heading"
    BLANK = "blank"
    UNORDERED_LIST_ITEM = "unordered_list_item"
    ORDERED_LIST_ITEM = "ordered_list_item"
    FENCED_CODE_START = "fenced_code_start"
    FENCED_CODE_END = "fenced_code_end"
    CODE_LINE = "code_line"
    PARAGRAPH = "paragraph"
    RAW = "raw"


@dataclass
class Block:
    """A single parsed line with its original text and classification."""

    line_number: int
    text: str
    block_type: BlockType
    heading_level: int | None = None


@dataclass
class Document:
    """Parsed document produced by the line-oriented parser."""

    blocks: list[Block] = field(default_factory=list)
    has_unclosed_code_fence: bool = False


@dataclass
class ValidationMessage:
    """A validation warning or error."""

    level: str
    message: str
    line_number: int | None = None


@dataclass
class NormalizationChange:
    """A single normalization rule application."""

    line_number: int
    rule: str
    description: str
    before: str
    after: str


@dataclass
class NormalizationReport:
    """Summary of a normalization run."""

    input_path: str | None = None
    output_path: str | None = None
    warnings: list[ValidationMessage] = field(default_factory=list)
    errors: list[ValidationMessage] = field(default_factory=list)
    changes: list[NormalizationChange] = field(default_factory=list)
