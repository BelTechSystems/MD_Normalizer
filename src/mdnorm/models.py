# Copyright (c) 2026 BelTech Systems LLC
# SPDX-License-Identifier: MIT

"""Shared data models for parsed and normalized documents."""

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
