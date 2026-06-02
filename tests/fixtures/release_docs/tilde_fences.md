# Tilde Fence Behavior

The MD Normalizer parser recognises only backtick fences (```). Tilde
fences (~~~) are classified as paragraph text rather than code block
markers. This is a known limitation documented in docs/release_testing.md.

## Implication for Checker Rules

Content inside tilde fences is not excluded from check rules MDQ005,
MDQ008, and MDQ009. A tilde-fenced block is treated as a sequence of
paragraph lines, so any violations within it will be reported.

## Example

The following uses tilde fences and contains only clean content so this
document remains finding-free despite the parser limitation:

~~~text
This is inside a tilde fence.
The checker cannot tell it is a code block.
No task annotations, no trailing whitespace, no excessive blank lines.
~~~

## Workaround

Use backtick fences for all code blocks to ensure the checker correctly
excludes their contents from analysis.
