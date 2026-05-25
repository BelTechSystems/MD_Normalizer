# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

### Notes

- Version 0.1.0 is an early-stage baseline focused on deterministic formatting.
- AI-assisted normalization, template enforcement, and publishing exports are out of scope for this release.

[0.1.0]: https://github.com/BelTechSystems/MD_Normalizer/releases/tag/v0.1.0
