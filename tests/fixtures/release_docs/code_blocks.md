# Code Block Preservation

This document verifies that content inside fenced code blocks is excluded
from checker rules MDQ005, MDQ008, and MDQ009.

## Python Example

The following block contains a task annotation and trailing whitespace on one
line. Neither should trigger MDQ005 or MDQ009 because they are inside a fence.

```python
# TODO: this annotation is inside a code block and must not trigger MDQ005
def process():
    pass  
```

## Text Example

The following block contains excessive blank lines and trailing whitespace.
These must not trigger MDQ008 or MDQ009 because they are inside a fence.

```text


extra blank lines inside the code block are not scanned


trailing spaces inside the block   
```

## Clean Section

This section contains only regular text outside any fenced block.
It has no task annotations, no excessive blank lines, and no trailing
whitespace, so no findings are expected here either.
