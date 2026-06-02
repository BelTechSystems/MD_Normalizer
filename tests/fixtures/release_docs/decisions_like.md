# Project Decisions

Formalizes architectural and implementation decisions.

## D-001: Use a Standalone CLI

Use a standalone command-line interface as the primary integration point.

Rationale: Keeps the tool independently testable and deployable without
requiring a library integration layer.

## D-002: Use Deterministic Rules

Use deterministic normalization rules rather than AI-assisted inference.

Rationale: Predictable, repeatable output is the primary value for version
control and review workflows.

## D-003: Preserve User Content

Do not rewrite prose or semantic content.

Rationale: The tool is a formatter, not an editor. Users retain authorship
over the meaning of their documents.
