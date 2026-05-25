
### `PLAN.md`

```markdown
# MD Normalizer Implementation Plan

## Milestone 1: Project Skeleton

Create a Python package with CLI entry point, initial module structure, pytest setup, and example files.

Acceptance criteria:

- `python -m pytest -q` runs successfully.
- `mdnorm --help` works after editable install.
- Package imports successfully.

## Milestone 2: File I/O and Safety

Implement input reading, output writing, overwrite protection, and dry-run behavior.

Acceptance criteria:

- Missing input files fail clearly.
- Empty files fail clearly.
- Existing output files are not overwritten unless `--force` is used.
- Dry-run does not write files.

## Milestone 3: Parser Baseline

Implement a lightweight line-oriented parser that recognizes:

- Headings
- Blank lines
- Paragraph lines
- Fenced code blocks
- List items
- Other raw lines

Acceptance criteria:

- Code fence state is tracked.
- Code block contents are preserved.
- Unclosed code fences are reported.

## Milestone 4: Deterministic Normalizer

Implement normalization rules:

- Remove trailing whitespace outside code blocks.
- Normalize blank lines around headings.
- Normalize unordered list markers to `-`.
- Normalize simple numbered lists.
- Preserve code block contents exactly.

Acceptance criteria:

- Output is stable across repeated runs.
- Applying normalization twice produces identical output.
- Code blocks are not modified.

## Milestone 5: Validator

Implement validation checks:

- Empty document detection.
- Unclosed code fence detection.
- Malformed heading detection.
- Trailing whitespace detection.
- Basic heading jump warning.

Acceptance criteria:

- Validation returns structured warnings and errors.
- CLI exits nonzero on validation errors.
- CLI prints useful messages.

## Milestone 6: Report Generation

Implement optional normalization report data structure.

Acceptance criteria:

- Normalizer records rule applications.
- Report can be serialized to JSON.
- Report includes input path, output path, warnings, errors, and changes.

## Milestone 7: README and Examples

Document installation, CLI usage, examples, and limitations.

Acceptance criteria:

- README includes quick start.
- Examples can be run manually.
- Version 0.1 limitations are explicit.