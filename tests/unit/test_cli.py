"""CLI smoke tests."""

import json
from pathlib import Path

import pytest

from mdnorm.cli import main


def test_help_exits_successfully(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["--help"])

    assert exc_info.value.code == 0

    captured = capsys.readouterr()
    assert "usage:" in captured.out
    assert "mdnorm" in captured.out
    assert "normalize" in captured.out
    assert "validate" in captured.out


def test_normalize_writes_output_file(tmp_path: Path) -> None:
    input_file = tmp_path / "rough.md"
    output_file = tmp_path / "clean.md"
    input_file.write_text("# Title\n\nBody\n", encoding="utf-8")

    exit_code = main(
        ["normalize", "--in", str(input_file), "--out", str(output_file)]
    )

    assert exit_code == 0
    assert output_file.read_text(encoding="utf-8") == "# Title\n\nBody\n"


def test_normalize_rejects_missing_input(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    missing = tmp_path / "missing.md"
    output_file = tmp_path / "clean.md"

    exit_code = main(
        ["normalize", "--in", str(missing), "--out", str(output_file)]
    )

    assert exit_code == 1
    captured = capsys.readouterr()
    assert "Input file not found" in captured.err
    assert not output_file.exists()


def test_normalize_rejects_empty_input(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    input_file = tmp_path / "empty.md"
    output_file = tmp_path / "clean.md"
    input_file.write_text("", encoding="utf-8")

    exit_code = main(
        ["normalize", "--in", str(input_file), "--out", str(output_file)]
    )

    assert exit_code == 1
    captured = capsys.readouterr()
    assert "Input file is empty" in captured.err
    assert not output_file.exists()


def test_normalize_refuses_existing_output_without_force(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    input_file = tmp_path / "rough.md"
    output_file = tmp_path / "clean.md"
    input_file.write_text("# Title\n", encoding="utf-8")
    output_file.write_text("existing", encoding="utf-8")

    exit_code = main(
        ["normalize", "--in", str(input_file), "--out", str(output_file)]
    )

    assert exit_code == 1
    captured = capsys.readouterr()
    assert "Output file already exists" in captured.err
    assert output_file.read_text(encoding="utf-8") == "existing"


def test_normalize_overwrites_with_force(tmp_path: Path) -> None:
    input_file = tmp_path / "rough.md"
    output_file = tmp_path / "clean.md"
    input_file.write_text("# Updated\n", encoding="utf-8")
    output_file.write_text("existing", encoding="utf-8")

    exit_code = main(
        [
            "normalize",
            "--in",
            str(input_file),
            "--out",
            str(output_file),
            "--force",
        ]
    )

    assert exit_code == 0
    assert output_file.read_text(encoding="utf-8") == "# Updated\n"


def test_normalize_dry_run_does_not_write(tmp_path: Path) -> None:
    input_file = tmp_path / "rough.md"
    output_file = tmp_path / "clean.md"
    input_file.write_text("# Title\n", encoding="utf-8")

    exit_code = main(
        [
            "normalize",
            "--in",
            str(input_file),
            "--out",
            str(output_file),
            "--dry-run",
        ]
    )

    assert exit_code == 0
    assert not output_file.exists()


def test_normalize_writes_json_report(tmp_path: Path) -> None:
    input_file = tmp_path / "rough.md"
    output_file = tmp_path / "clean.md"
    report_file = tmp_path / "normalization_report.json"
    input_file.write_text("* item  \n# Title\n### Section\n", encoding="utf-8")

    exit_code = main(
        [
            "normalize",
            "--in",
            str(input_file),
            "--out",
            str(output_file),
            "--report",
            str(report_file),
        ]
    )

    assert exit_code == 0
    payload = json.loads(report_file.read_text(encoding="utf-8"))
    assert payload["input_path"] == str(input_file)
    assert payload["output_path"] == str(output_file)
    assert any(change["rule"] == "unordered_list_marker" for change in payload["changes"])
    assert any(
        warning["message"] == "Heading level jumps from 1 to 3."
        for warning in payload["warnings"]
    )


def test_normalize_dry_run_writes_report_but_not_output(tmp_path: Path) -> None:
    input_file = tmp_path / "rough.md"
    output_file = tmp_path / "clean.md"
    report_file = tmp_path / "normalization_report.json"
    input_file.write_text("* item\n", encoding="utf-8")

    exit_code = main(
        [
            "normalize",
            "--in",
            str(input_file),
            "--out",
            str(output_file),
            "--dry-run",
            "--report",
            str(report_file),
        ]
    )

    assert exit_code == 0
    assert not output_file.exists()
    assert report_file.exists()


def test_normalize_report_refuses_existing_file_without_force(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    input_file = tmp_path / "rough.md"
    output_file = tmp_path / "clean.md"
    report_file = tmp_path / "normalization_report.json"
    input_file.write_text("# Title\n", encoding="utf-8")
    report_file.write_text("{}", encoding="utf-8")

    exit_code = main(
        [
            "normalize",
            "--in",
            str(input_file),
            "--out",
            str(output_file),
            "--report",
            str(report_file),
        ]
    )

    assert exit_code == 1
    captured = capsys.readouterr()
    assert "Output file already exists" in captured.err
    assert report_file.read_text(encoding="utf-8") == "{}"


def test_validate_passes_for_clean_markdown(tmp_path: Path) -> None:
    input_file = tmp_path / "clean.md"
    input_file.write_text("# Title\n\nBody\n", encoding="utf-8")

    exit_code = main(["validate", "--in", str(input_file)])

    assert exit_code == 0


def test_validate_reports_errors_and_exits_nonzero(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    input_file = tmp_path / "rough.md"
    input_file.write_text("#Title\n", encoding="utf-8")

    exit_code = main(["validate", "--in", str(input_file)])

    assert exit_code == 1
    captured = capsys.readouterr()
    assert "error: line 1: Malformed heading." in captured.err


def test_validate_rejects_missing_input(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    missing = tmp_path / "missing.md"

    exit_code = main(["validate", "--in", str(missing)])

    assert exit_code == 1
    captured = capsys.readouterr()
    assert "Input file not found" in captured.err
