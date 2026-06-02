# MD Normalizer

MD Normalizer is a deterministic Markdown cleanup CLI from BelTech Systems LLC. It converts rough text, copied AI output, or inconsistent Markdown into clean, predictable Markdown documents.

The baseline is fully deterministic and does not use AI. It preserves user-authored prose and fenced code block contents exactly while applying repeatable formatting rules for spacing, list markers, and heading layout.

**Command overview:**

| Command | Purpose |
| --- | --- |
| `normalize` | Cleans Markdown formatting deterministically. |
| `validate` | Detects structural Markdown errors (empty document, unclosed fences, malformed headings). |
| `check` | Reports engineering-document quality findings. Advisory only — never modifies the file. |

Important defaults:

- Fenced code block contents are preserved.
- Existing output files are not overwritten unless `--force` is used.
- On Windows, if `mdnorm` is not on `PATH`, use `python -m mdnorm`.

License: [MIT](LICENSE)

## Installation

Install the package locally in editable mode for development:

```bash
python -m pip install -e ".[dev]"
```

This installs the `mdnorm` CLI and pytest for running the test suite.

### Windows troubleshooting

On Windows, a user-level install may place `mdnorm.exe` in the Python user Scripts directory, which is often not on `PATH`. You may see a pip warning like:

```text
The script mdnorm.exe is installed in '...\Python313\Scripts' which is not on PATH.
```

Recommended options:

1. Use a project virtual environment, activate it, then install and run the tool:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   python -m pip install -e ".[dev]"
   mdnorm --help
   ```

2. Invoke the CLI through Python when `mdnorm` is not found:

   ```bash
   python -m mdnorm --help
   python -m mdnorm normalize --in examples/rough_ai_output.md --out output/clean.md
   python -m mdnorm validate --in output/clean.md
   ```

   `python -m mdnorm.cli` is also supported.

## Quick Start

Normalize a rough Markdown file:

```bash
mdnorm normalize --in examples/rough_ai_output.md --out output/clean.md
```

Validate normalized output:

```bash
mdnorm validate --in output/clean.md
```

Check a document for quality findings:

```bash
mdnorm check --in README.md
```

Write a JSON normalization report:

```bash
mdnorm normalize \
  --in examples/rough_ai_output.md \
  --out output/clean.md \
  --report output/normalization_report.json
```

## CLI Examples

```bash
# Basic normalization
mdnorm normalize --in examples/rough_ai_output.md --out output/clean.md

# Overwrite an existing output file
mdnorm normalize --in examples/rough_ai_output.md --out output/clean.md --force

# Preview changes without writing output
mdnorm normalize --in examples/rough_notes.txt --out output/clean.md --dry-run

# Validate a Markdown file
mdnorm validate --in examples/expected_clean.md

# Check a document for quality findings (advisory; does not modify the file)
mdnorm check --in README.md

# Write check findings to a JSON report
mdnorm check --in README.md --report output/check_report.json

# Exit 1 when warning-level findings are present (useful in CI)
mdnorm check --in README.md --strict
```

## Example Before and After

**Before** (`examples/rough_ai_output.md`):

```markdown
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
```

```python
def normalize(text: str) -> str:
    return text.strip() + "   "
```

**After** (`examples/expected_clean.md`):

```markdown
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
```

```python
def normalize(text: str) -> str:
    return text.strip() + "   "
```

This example demonstrates:

- Heading blank-line cleanup
- Unordered list marker normalization to `-`
- Ordered list renumbering
- Repeated blank-line reduction
- Exact preservation of fenced code block contents, including trailing spaces inside the block

A second sample input is available at `examples/rough_notes.txt`.

## Advisory Check Command

`mdnorm check` analyzes a Markdown file for common engineering-document quality issues.
It is purely advisory: it never modifies the input file, rewrites prose, or enforces templates.

```bash
# Basic check (exits 0; prints findings or "No document quality findings.")
python -m mdnorm check --in README.md

# Write findings to a JSON report
python -m mdnorm check --in README.md --report output/check_report.json

# Exit 1 when warning-level findings exist (CI gate)
python -m mdnorm check --in README.md --strict
```

### Check Rules (v0.2.0)

| Rule | Level | Trigger |
| --- | --- | --- |
| MDQ001 | WARNING | Missing top-level H1 heading |
| MDQ002 | WARNING | Multiple top-level H1 headings |
| MDQ003 | WARNING | Duplicate heading text |
| MDQ004 | INFO | Empty section (heading followed by another heading or EOF) |
| MDQ005 | INFO | Open task annotation outside code blocks |
| MDQ006 | INFO | Fenced code block missing language tag |
| MDQ007 | WARNING | Broken local Markdown link (relative path does not exist) |
| MDQ008 | INFO | More than two consecutive blank lines outside code blocks |
| MDQ009 | INFO | Trailing whitespace outside code block |

Fenced code block contents are excluded from all applicable rules.

## Version 0.2 Scope

Version 0.2 adds:

- `mdnorm check` advisory document-quality command
- Nine check rules (MDQ001–MDQ009)
- JSON check report output via `--report`
- Strict mode via `--strict` (warning-level findings → exit 1)

## Version 0.1 Scope

Version 0.1 includes:

- `mdnorm normalize` for deterministic Markdown cleanup
- `mdnorm validate` for basic Markdown checks
- Optional JSON normalization reports via `--report`
- Line-oriented parsing for headings, lists, paragraphs, and fenced code blocks
- Safety rules for missing input, empty input, overwrite protection, and dry-run mode

Validation in 0.1 checks for:

- Empty documents
- Unclosed fenced code blocks
- Malformed headings
- Trailing whitespace outside code blocks
- Heading level jump warnings

## Non-Goals

The following remain out of scope:

- Template enforcement
- AI-assisted rewriting or semantic editing
- Automatic section inference or reordering
- PDF, DOCX, or HTML export
- Project-level configuration files
- Rewriting prose or reformatting code inside fenced blocks

## Testing

Run the test suite with:

```bash
python -m pytest -q
```

## Example Files

| File | Purpose |
| --- | --- |
| `examples/rough_ai_output.md` | Rough AI-style Markdown input |
| `examples/rough_notes.txt` | Plain-text notes with Markdown-like structure |
| `examples/expected_clean.md` | Expected normalized output for `rough_ai_output.md` |

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).

Copyright (c) 2026 BelTech Systems LLC.

## Related Docs

- `PROJECT.md` — product and pipeline overview
- `PLAN.md` — implementation milestones
- `CHANGELOG.md` — release history
- `docs/decisions/DECISIONS.md` — project decisions
