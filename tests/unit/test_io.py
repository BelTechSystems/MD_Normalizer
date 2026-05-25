"""Tests for file I/O helpers."""

from pathlib import Path

import pytest

from mdnorm.io import (
    EmptyInputError,
    InputNotFoundError,
    OutputExistsError,
    read_input,
    write_output,
)


def test_read_input_returns_file_contents(tmp_path: Path) -> None:
    input_file = tmp_path / "rough.md"
    input_file.write_text("# Title\n\nBody\n", encoding="utf-8")

    assert read_input(input_file) == "# Title\n\nBody\n"


def test_read_input_rejects_missing_file(tmp_path: Path) -> None:
    missing = tmp_path / "missing.md"

    with pytest.raises(InputNotFoundError, match="Input file not found"):
        read_input(missing)


def test_read_input_rejects_empty_file(tmp_path: Path) -> None:
    empty = tmp_path / "empty.md"
    empty.write_text("", encoding="utf-8")

    with pytest.raises(EmptyInputError, match="Input file is empty"):
        read_input(empty)


def test_read_input_rejects_whitespace_only_file(tmp_path: Path) -> None:
    whitespace = tmp_path / "blank.md"
    whitespace.write_text("   \n\t\n", encoding="utf-8")

    with pytest.raises(EmptyInputError, match="Input file is empty"):
        read_input(whitespace)


def test_write_output_creates_file(tmp_path: Path) -> None:
    output_file = tmp_path / "clean.md"

    write_output(output_file, "# Title\n")

    assert output_file.read_text(encoding="utf-8") == "# Title\n"


def test_write_output_refuses_existing_file_without_force(tmp_path: Path) -> None:
    output_file = tmp_path / "clean.md"
    output_file.write_text("existing", encoding="utf-8")

    with pytest.raises(OutputExistsError, match="Output file already exists"):
        write_output(output_file, "new content")


def test_write_output_overwrites_with_force(tmp_path: Path) -> None:
    output_file = tmp_path / "clean.md"
    output_file.write_text("existing", encoding="utf-8")

    write_output(output_file, "updated", force=True)

    assert output_file.read_text(encoding="utf-8") == "updated"


def test_write_output_dry_run_does_not_write(tmp_path: Path) -> None:
    output_file = tmp_path / "clean.md"

    write_output(output_file, "would write", dry_run=True)

    assert not output_file.exists()


def test_write_output_dry_run_does_not_overwrite_existing(tmp_path: Path) -> None:
    output_file = tmp_path / "clean.md"
    output_file.write_text("existing", encoding="utf-8")

    write_output(output_file, "updated", force=True, dry_run=True)

    assert output_file.read_text(encoding="utf-8") == "existing"
