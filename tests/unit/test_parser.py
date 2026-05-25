"""Tests for the line-oriented parser."""

from mdnorm.models import BlockType
from mdnorm.parser import parse


def test_heading_detection() -> None:
    document = parse("# Title\n## Section\n### Subsection\n")

    headings = [block for block in document.blocks if block.block_type == BlockType.HEADING]
    assert len(headings) == 3
    assert headings[0].text == "# Title"
    assert headings[0].heading_level == 1
    assert headings[1].text == "## Section"
    assert headings[1].heading_level == 2
    assert headings[2].text == "### Subsection"
    assert headings[2].heading_level == 3


def test_unordered_list_item_detection() -> None:
    document = parse("- first\n* second\n+ third\n")

    items = [
        block
        for block in document.blocks
        if block.block_type == BlockType.UNORDERED_LIST_ITEM
    ]
    assert len(items) == 3
    assert items[0].text == "- first"
    assert items[1].text == "* second"
    assert items[2].text == "+ third"


def test_ordered_list_item_detection() -> None:
    document = parse("1. first\n2) second\n10. tenth\n")

    items = [
        block
        for block in document.blocks
        if block.block_type == BlockType.ORDERED_LIST_ITEM
    ]
    assert len(items) == 3
    assert items[0].text == "1. first"
    assert items[1].text == "2) second"
    assert items[2].text == "10. tenth"


def test_fenced_code_block_detection() -> None:
    document = parse("```python\nprint('hi')\n```\n")

    types = [block.block_type for block in document.blocks]
    assert types == [
        BlockType.FENCED_CODE_START,
        BlockType.CODE_LINE,
        BlockType.FENCED_CODE_END,
    ]
    assert document.blocks[0].text == "```python"
    assert document.has_unclosed_code_fence is False


def test_code_block_content_preservation() -> None:
    source = "```\n  indented\n# not a heading\n- not a list\n```\n"
    document = parse(source)

    code_lines = [
        block for block in document.blocks if block.block_type == BlockType.CODE_LINE
    ]
    assert [block.text for block in code_lines] == [
        "  indented",
        "# not a heading",
        "- not a list",
    ]


def test_unclosed_code_fence_detection() -> None:
    document = parse("# Title\n\n```python\nprint('hi')\n")

    assert document.has_unclosed_code_fence is True
    assert document.blocks[-1].block_type == BlockType.CODE_LINE
    assert document.blocks[-1].text == "print('hi')"
