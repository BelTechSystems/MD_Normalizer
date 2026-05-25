# Copyright (c) 2026 BelTech Systems LLC
# SPDX-License-Identifier: MIT

"""Input and output file handling."""

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
