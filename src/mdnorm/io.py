# ============================================================
# FILE:          io.py
# PROJECT:       MD Normalizer
# BRIEF:         Provides UTF-8 input reading and output writing with overwrite safety.
# DOCUMENT:      docs/tool_framework.md; README.md
# REQUIREMENTS:  support-only; no formal requirement IDs assigned for v0.1.0
# COPYRIGHT:     Copyright (c) 2026 BelTech Systems LLC.
# LICENSE:       MIT License; see LICENSE in repository root.
# CLASSIFICATION: OPEN-SOURCE
# STANDARD:      Python 3.11+
# FUNCTIONS/CLASSES:
#   read_input(path)
#     Reads and validates input file content.
#   write_output(path, content, force, dry_run)
#     Writes output with overwrite and dry-run protection.
#   IoError, InputNotFoundError, EmptyInputError, OutputExistsError
#     File I/O exception types.
# DEPENDENCIES:
#   Standard library: pathlib
#   Third-party:      none
#   Internal:         none
# PORTABILITY:    Supports Python 3.11 or later on Windows, Linux, and macOS.
# IMPL. STATUS:   IN_REVIEW
# HISTORY:
#   2026-05-25  Cursor    [DOCS] Replaced minimal SPDX header with STD-006 style metadata header
#   2026-05-25  Cursor    [DOCS] Standardized FUNCTIONS/CLASSES label and section ordering
# ============================================================

"""Input and output file handling.

The file header above is the authoritative engineering metadata source for
this module.
"""

from __future__ import annotations

from pathlib import Path


class IoError(Exception):
    """Base class for file I/O errors."""


class InputNotFoundError(IoError, FileNotFoundError):
    """Raised when the input file does not exist."""


class EmptyInputError(IoError, ValueError):
    """Raised when the input file has no content."""


class OutputExistsError(IoError, FileExistsError):
    """Raised when the output file exists and overwrite was not requested."""


def read_input(path: str | Path) -> str:
    """Read UTF-8 text from an input file."""
    input_path = Path(path)

    if not input_path.is_file():
        raise InputNotFoundError(f"Input file not found: {input_path}")

    text = input_path.read_text(encoding="utf-8")
    if not text.strip():
        raise EmptyInputError(f"Input file is empty: {input_path}")

    return text


def write_output(
    path: str | Path,
    content: str,
    *,
    force: bool = False,
    dry_run: bool = False,
) -> None:
    """Write UTF-8 text to an output file."""
    output_path = Path(path)

    if output_path.exists() and not force:
        raise OutputExistsError(
            f"Output file already exists: {output_path}. Use --force to overwrite."
        )

    if dry_run:
        return

    output_path.write_text(content, encoding="utf-8")
