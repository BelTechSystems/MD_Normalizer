# Markdown Normalizer

AI output often looks like markdown but is not consistently formatted.

## Users

- engineers
- technical writers
- developers

## Workflow

1. parse
2. normalize
3. validate

```python
def normalize(text: str) -> str:
    return text.strip() + "   "
```
