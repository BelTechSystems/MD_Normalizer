"""Tests for normalization report generation."""

import json
from pathlib import Path

from mdnorm.models import NormalizationChange, NormalizationReport, ValidationMessage
from mdnorm.reporter import report_to_dict, serialize_report, write_report


def test_report_to_dict_includes_required_fields() -> None:
    report = NormalizationReport(
        input_path="rough.md",
        output_path="clean.md",
        warnings=[
            ValidationMessage(
                level="warning",
                message="Heading level jumps from 1 to 3.",
                line_number=3,
            )
        ],
        errors=[
            ValidationMessage(
                level="error",
                message="Trailing whitespace is not allowed.",
                line_number=5,
            )
        ],
        changes=[
            NormalizationChange(
                line_number=2,
                rule="unordered_list_marker",
                description="Normalize unordered list marker to '-'",
                before="* item",
                after="- item",
            )
        ],
    )

    payload = report_to_dict(report)

    assert payload == {
        "input_path": "rough.md",
        "output_path": "clean.md",
        "warnings": [
            {
                "level": "warning",
                "message": "Heading level jumps from 1 to 3.",
                "line_number": 3,
            }
        ],
        "errors": [
            {
                "level": "error",
                "message": "Trailing whitespace is not allowed.",
                "line_number": 5,
            }
        ],
        "changes": [
            {
                "line_number": 2,
                "rule": "unordered_list_marker",
                "description": "Normalize unordered list marker to '-'",
                "before": "* item",
                "after": "- item",
            }
        ],
    }


def test_serialize_report_produces_json() -> None:
    report = NormalizationReport(input_path="rough.md", output_path="clean.md")
    payload = json.loads(serialize_report(report))

    assert payload["input_path"] == "rough.md"
    assert payload["output_path"] == "clean.md"
    assert payload["warnings"] == []
    assert payload["errors"] == []
    assert payload["changes"] == []


def test_write_report_creates_json_file(tmp_path: Path) -> None:
    report_path = tmp_path / "normalization_report.json"
    report = NormalizationReport(
        input_path="rough.md",
        output_path="clean.md",
        changes=[
            NormalizationChange(
                line_number=1,
                rule="trailing_whitespace",
                description="Remove trailing whitespace",
                before="text   ",
                after="text",
            )
        ],
    )

    write_report(report_path, report)

    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert payload["input_path"] == "rough.md"
    assert payload["output_path"] == "clean.md"
    assert len(payload["changes"]) == 1
