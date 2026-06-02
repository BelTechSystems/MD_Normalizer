# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.1] - 2026-06-02

### Added

- `scripts/release_check.ps1` repeatable PowerShell release verification script.
- `docs/release_testing.md` release testing documentation.
- Fixture Markdown files under `tests/fixtures/release_docs/` for checker regression testing.
- Fixture-based pytest tests in `tests/unit/test_checker_fixtures.py`.
- Explicit tilde-fence limitation test documenting that `~~~` blocks are not excluded from check rules.

### Fixed

- MDQ003 false positives: duplicate subsection names (e.g. `### Added`) under different parent sections no longer trigger the rule. Scope is now tracked per ancestor-heading context.
- MDQ004 false positives: a heading followed immediately by a child heading (deeper level) is no longer reported as empty. Only headings at the same or higher level trigger the rule.
- MDQ005/MDQ006 false positives in README: restructured nested Markdown examples to use separate tagged code blocks, eliminating parser confusion from 4-backtick outer fences.

### Changed

- `output/` added to `.gitignore` so release-check output files are not committed.
- `scripts/release_check.ps1` explicitly excluded from the `*.ps1` gitignore pattern.

### Notes

- Tilde fences (`~~~`) are a known limitation: the parser does not recognise them, so their contents are not excluded from checker rules. Documented in `docs/release_testing.md`.
- No new product commands or features added; this release is purely hardening and tooling.

## [0.2.0] - 2026-06-02

### Added

- `mdnorm check` advisory document-quality command.
- Nine initial check rules: MDQ001–MDQ009.
  - MDQ001: Missing top-level H1 heading (WARNING).
  - MDQ002: Multiple top-level H1 headings (WARNING).
  - MDQ003: Duplicate heading text (WARNING).
  - MDQ004: Empty section (INFO).
  - MDQ005: Open task annotation marker present outside code blocks (INFO).
  - MDQ006: Fenced code block missing language tag (INFO).
  - MDQ007: Broken local Markdown link (WARNING).
  - MDQ008: Excessive consecutive blank lines outside code blocks (INFO).
  - MDQ009: Trailing whitespace outside code block (INFO).
- `--strict` option for `check`: exit 1 when warning-level findings are present.
- `--report PATH` option for `check`: write findings to a JSON report file.
- `--force` option for `check`: overwrite an existing report file.
- `CheckFinding` and `CheckReport` dataclasses in `models.py`.
- `checker.py` module with all rule implementations.
- Check report JSON serialization in `reporter.py` (`write_check_report`).
- Unit tests for all nine check rules and CLI behavior.

### Notes

- The `check` command is purely advisory; it does not modify the input file.
- Fenced code block contents are excluded from all applicable rules.
- MDQ007 (broken local links) is skipped when no input path is provided.

## [0.1.0] - 2026-05-24

### Added

- Initial public open-source release under the MIT License.
- Copyright (c) 2026 BelTech Systems LLC.
- `mdnorm normalize` for deterministic Markdown cleanup.
- `mdnorm validate` for baseline Markdown validation.
- Optional JSON normalization reports via `--report`.
- Line-oriented parser for headings, lists, paragraphs, and fenced code blocks.
- Safety rules for missing input, empty input, overwrite protection, and dry-run mode.
- Module-based CLI invocation via `python -m mdnorm` and `python -m mdnorm.cli`.
- Example inputs and expected output under `examples/`.
- Pytest test suite covering I/O, parsing, normalization, validation, reporting, and CLI behavior.

### Changed

- Upgraded Python source headers under `src/mdnorm/` to BelTech-STD-006 style metadata headers.

### Notes

- Version 0.1.0 is an early-stage baseline focused on deterministic formatting.
- AI-assisted normalization, template enforcement, and publishing exports are out of scope for this release.

[0.2.1]: https://github.com/BelTechSystems/MD_Normalizer/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/BelTechSystems/MD_Normalizer/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/BelTechSystems/MD_Normalizer/releases/tag/v0.1.0
