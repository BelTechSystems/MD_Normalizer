# Release Testing

This document describes how to set up a virtual environment, install MD Normalizer
in editable mode, and run the repeatable release verification script before tagging
a new version.

## Prerequisites

- Python 3.11 or later on PATH.
- PowerShell 5.1 or later (Windows) or PowerShell 7+ (cross-platform).
- Run all commands from the **repository root**.

## 1. Virtual Environment Setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Or on Linux/macOS:

```bash
python -m venv .venv
source .venv/bin/activate
```

## 2. Editable Install

```powershell
pip install -e ".[dev]"
```

This installs `mdnorm` and all development dependencies (pytest) in editable
mode so the installed CLI reflects the current source tree.

## 3. Running the Release Check Script

Run from the repository root with a process-scoped execution-policy bypass so
the script does not require a permanent policy change:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\release_check.ps1
```

Or if you are already inside a PowerShell session with the virtual environment
active:

```powershell
. .\.venv\Scripts\Activate.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\release_check.ps1
```

### PowerShell Execution Policy Note

Windows PowerShell blocks unsigned scripts by default.
`-ExecutionPolicy Bypass` applies only to that process invocation and does not
change the machine-wide or user-level policy.

## 4. What the Script Verifies

The script runs each check in order and reports `[PASS]` or `[FAIL]` for every
step.  Steps:

| Step | Command | Assertion |
|------|---------|-----------|
| 1    | `python -m pytest -q` | All tests pass |
| 2    | `python -m mdnorm --help` | Exit 0 |
| 3    | `normalize --force --report` | Exit 0; `output/clean.md` and `output/normalization_report.json` created |
| 4    | Overwrite protection | `normalize` without `--force` is rejected (non-zero exit) |
| 5    | `validate output/clean.md` | Exit 0 |
| 6    | `check README.md --strict` | Exit 0 (no warning-level findings) |
| 6    | `check CHANGELOG.md --strict` | Exit 0 |
| 6    | `check docs/decisions/DECISIONS.md --strict` | Exit 0 |
| 7    | `check --report --force` | Exit 0; `output/check_report.json` created |

A final summary line prints `Release check PASSED` or `Release check FAILED`
with a count of failures.

## 5. Expected Successful Output

```text
MD Normalizer Release Check
============================
  Working directory : E:\...\MD_Normalizer
  Python            : Python 3.11.x

Step 1: Automated tests
----------------------------------------------------------------------
... passed
  [PASS] pytest -q

Step 2: CLI help
----------------------------------------------------------------------
  [PASS] mdnorm --help

Step 3: Normalize with report
----------------------------------------------------------------------
  [PASS] normalize --force --report
  [PASS] File exists: output/clean.md
  [PASS] File exists: output/normalization_report.json

Step 4: Overwrite protection
----------------------------------------------------------------------
  [PASS] normalize without --force (must reject existing output)  (correctly rejected, exit 1)

Step 5: Validate normalized output
----------------------------------------------------------------------
  [PASS] validate output/clean.md

Step 6: Check project documents (--strict)
----------------------------------------------------------------------
No document quality findings.
  [PASS] check README.md --strict
No document quality findings.
  [PASS] check CHANGELOG.md --strict
No document quality findings.
  [PASS] check docs/decisions/DECISIONS.md --strict

Step 7: Check with JSON report
----------------------------------------------------------------------
No document quality findings.
  [PASS] check README.md --report --force
  [PASS] File exists: output/check_report.json

============================
Release check PASSED: all steps succeeded.
```

## 6. Generated Output Files

The script writes the following files to the `output/` directory:

| File | Description |
|------|-------------|
| `output/clean.md` | Normalized output of `examples/rough_ai_output.md` |
| `output/normalization_report.json` | Normalization change report |
| `output/check_report.json` | Advisory check report for `README.md` |

**These files must not be committed.**  The `output/` directory is excluded by
`.gitignore`.

## 7. Known Limitations

### Tilde Fences Not Recognized

The MD Normalizer parser recognizes only backtick fences (` ``` `).
Tilde fences (`~~~`) are classified as paragraph text.

**Implication for `mdnorm check`:** Content inside tilde-fenced blocks is not
excluded from check rules MDQ005, MDQ008, and MDQ009.  A `TODO` marker or
trailing whitespace inside a `~~~` block will be reported.

**Workaround:** Use backtick fences for all fenced code blocks to ensure the
checker correctly excludes their contents from analysis.

**Test coverage:** The behavior is documented by explicit tests in
`tests/unit/test_checker.py` (`test_mdq006_tilde_fence_not_parsed_bare`,
`test_mdq006_tilde_fence_not_parsed_with_language`) and in
`tests/unit/test_checker_fixtures.py` (`test_tilde_fence_limitation_content_is_not_excluded`).

### Nested Markdown Examples

The parser does not support four-backtick outer fences containing three-backtick
inner fences.  The inner closing fence is misclassified as a new opening fence
without a language tag, which triggers MDQ006.

**Workaround:** Use separate adjacent code blocks — one tagged `markdown`, one
tagged with the inner language — instead of nesting fences.

## 8. Manual Verification

After the release script passes, also verify manually:

```powershell
python -m mdnorm normalize --in examples/rough_ai_output.md --out output/clean.md --force
python -m mdnorm validate --in output/clean.md
python -m mdnorm check --in README.md --strict
python -m mdnorm check --in CHANGELOG.md --strict
python -m mdnorm check --in docs/decisions/DECISIONS.md --strict
```
