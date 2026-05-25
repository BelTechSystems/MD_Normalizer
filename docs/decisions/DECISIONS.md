# MD Normalizer Decisions

## D-001: Standalone CLI First

MD Normalizer shall be developed first as a standalone Python CLI tool named `mdnorm`.

Rationale:
A standalone CLI keeps the tool independently testable and avoids coupling it too early to ArchForge or another larger system. Integration can be added later after the deterministic baseline is stable.

## D-002: Deterministic Rules Before AI Assistance

The baseline implementation shall use deterministic normalization rules only.

Rationale:
The primary value of the tool is predictable cleanup of Markdown-like text. AI-assisted restructuring may be useful later, but it should not be part of the foundation because it makes behavior harder to test and repeat.

## D-003: Preserve User Content

The tool shall preserve user-authored content unless a specific normalization rule applies.

Rationale:
Markdown cleanup should not silently become editing or rewriting. Any structural changes should be explainable through a report.

## D-004: Preserve Code Block Contents

The tool shall not modify the contents of fenced code blocks by default.

Rationale:
Code blocks may contain source code, logs, terminal output, configuration files, or examples. Reformatting them risks damaging meaningful content.

## D-005: Refuse Overwrite Unless Forced

The tool shall not overwrite an existing output file unless `--force` is used.

Rationale:
The tool is intended to support human review and safe document cleanup. Accidental overwrite would violate that workflow.

## D-006: Support Module Invocation for Windows-Friendly Usage

The CLI shall support `python -m mdnorm` and `python -m mdnorm.cli` in addition to the `mdnorm` console script.

Rationale:
On Windows, user-level installs may place `mdnorm.exe` outside `PATH`. Module invocation provides a reliable fallback without changing normalization behavior.

## D-007: Release v0.1.0 as Open Source Under BelTech Systems LLC

MD Normalizer v0.1.0 shall be released publicly under the MIT License with BelTech Systems LLC as the copyright holder at `https://github.com/BelTechSystems/MD_Normalizer`.

Rationale:
An early public release establishes the deterministic baseline, enables feedback, and documents project intent before adding optional AI-assisted or template-driven features.

## D-008: Adopt STD-006 Python Source Headers

Python source files under `src/mdnorm/` shall use structured BelTech-STD-006 style headers for project identity, open-source governance, dependency visibility, portability, lifecycle status, and append-only history.

Rationale:
Structured headers make each module reviewable, auditable, and machine-readable. They provide consistent engineering metadata without embedding long license text in source files.
