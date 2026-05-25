# Copyright (c) 2026 BelTech Systems LLC
# SPDX-License-Identifier: MIT

"""Line-oriented Markdown parser."""

from __future__ import annotations

import re

from mdnorm.models import Block, BlockType, Document

_HEADING_RE = re.compile(r"^(?P<level>#{1,6})\s+(?P<title>\S.*)$")
_UNORDERED_LIST_RE = re.compile(r"^\s*[-*+]\s+\S")
_ORDERED_LIST_RE = re.compile(r"^\s*\d+[.)]\s+\S")
_FENCE_RE = re.compile(r"^\s*```")
_RAW_RE = re.compile(
    r"^\s*(?:"
    r">|"  # blockquote
    r"\|.*\|"  # table row
    r"[-_*]{3,}\s*$"  # horizontal rule
    r")"
)


def parse(text: str) -> Document:
    """Parse text into a line-oriented document model."""
    lines = text.splitlines()
    blocks: list[Block] = []
    in_fence = False

    for line_number, line in enumerate(lines, start=1):
        block = _classify_line(line, line_number, in_fence)
        blocks.append(block)

        if block.block_type == BlockType.FENCED_CODE_START:
            in_fence = True
        elif block.block_type == BlockType.FENCED_CODE_END:
            in_fence = False

    return Document(
        blocks=blocks,
        has_unclosed_code_fence=in_fence,
    )


def _classify_line(line: str, line_number: int, in_fence: bool) -> Block:
    if not line.strip():
        return Block(line_number=line_number, text=line, block_type=BlockType.BLANK)

    if in_fence:
        if _FENCE_RE.match(line):
            return Block(
                line_number=line_number,
                text=line,
                block_type=BlockType.FENCED_CODE_END,
            )
        return Block(line_number=line_number, text=line, block_type=BlockType.CODE_LINE)

    if _FENCE_RE.match(line):
        return Block(
            line_number=line_number,
            text=line,
            block_type=BlockType.FENCED_CODE_START,
        )

    heading_match = _HEADING_RE.match(line)
    if heading_match:
        return Block(
            line_number=line_number,
            text=line,
            block_type=BlockType.HEADING,
            heading_level=len(heading_match.group("level")),
        )

    if _UNORDERED_LIST_RE.match(line):
        return Block(
            line_number=line_number,
            text=line,
            block_type=BlockType.UNORDERED_LIST_ITEM,
        )

    if _ORDERED_LIST_RE.match(line):
        return Block(
            line_number=line_number,
            text=line,
            block_type=BlockType.ORDERED_LIST_ITEM,
        )

    if _RAW_RE.match(line):
        return Block(line_number=line_number, text=line, block_type=BlockType.RAW)

    return Block(line_number=line_number, text=line, block_type=BlockType.PARAGRAPH)
