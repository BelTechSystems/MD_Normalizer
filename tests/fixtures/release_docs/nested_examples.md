# Nested Markdown Examples

This document demonstrates how to include Markdown code examples that
themselves contain code blocks, without triggering MDQ006 false positives.

## The Problem

Placing a three-backtick code block inside a four-backtick outer fence causes
the parser to misclassify the inner closing fence as a new opening fence
without a language tag. This triggers MDQ006.

## Recommended Pattern

Use separate adjacent code blocks instead of nesting fences.
Show the Markdown content in one block and any embedded code in another:

```markdown
# Example Heading

Some content here.
```

```python
def example_function():
    return "hello"
```

## Notes

The separate-block pattern above correctly labels both fences with language
tags. The parser sees two independent code blocks and no MDQ006 finding is
produced.
