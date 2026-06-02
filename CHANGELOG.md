# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

[0.2.0]: https://github.com/BelTechSystems/MD_Normalizer/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/BelTechSystems/MD_Normalizer/releases/tag/v0.1.0
