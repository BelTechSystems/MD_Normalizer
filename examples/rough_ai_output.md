# Markdown Normalizer   

AI output often looks like markdown but is not consistently formatted.


## Users
* engineers
+ technical writers
- developers


## Workflow
3. parse
5) normalize
7. validate


```python
def normalize(text: str) -> str:
    return text.strip() + "   "
```
