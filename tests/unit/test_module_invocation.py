"""Tests for module-based CLI invocation."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_PATH = PROJECT_ROOT / "src"


@pytest.fixture
def src_env() -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(
        [str(SRC_PATH), env.get("PYTHONPATH", "")]
    ).rstrip(os.pathsep)
    return env


def test_mdnorm_module_help(src_env: dict[str, str]) -> None:
    result = subprocess.run(
        [sys.executable, "-m", "mdnorm", "--help"],
        capture_output=True,
        text=True,
        env=src_env,
        check=False,
    )

    assert result.returncode == 0
    assert "usage:" in result.stdout
    assert "normalize" in result.stdout
    assert "validate" in result.stdout


def test_mdnorm_cli_module_help(src_env: dict[str, str]) -> None:
    result = subprocess.run(
        [sys.executable, "-m", "mdnorm.cli", "--help"],
        capture_output=True,
        text=True,
        env=src_env,
        check=False,
    )

    assert result.returncode == 0
    assert "usage:" in result.stdout
    assert "mdnorm" in result.stdout


def test_mdnorm_module_normalize(
    src_env: dict[str, str],
    tmp_path: Path,
) -> None:
    input_file = tmp_path / "rough.md"
    output_file = tmp_path / "clean.md"
    input_file.write_text("# Title\n\nBody\n", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "mdnorm",
            "normalize",
            "--in",
            str(input_file),
            "--out",
            str(output_file),
        ],
        capture_output=True,
        text=True,
        env=src_env,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert output_file.read_text(encoding="utf-8") == "# Title\n\nBody\n"


def test_mdnorm_module_validate(
    src_env: dict[str, str],
    tmp_path: Path,
) -> None:
    input_file = tmp_path / "clean.md"
    input_file.write_text("# Title\n\nBody\n", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "mdnorm",
            "validate",
            "--in",
            str(input_file),
        ],
        capture_output=True,
        text=True,
        env=src_env,
        check=False,
    )

    assert result.returncode == 0, result.stderr
