# Copyright (c) 2026 BelTech Systems LLC
# SPDX-License-Identifier: MIT

"""Normalization report generation."""

from __future__ import annotations

import json
from pathlib import Path

from mdnorm.io import write_output
from mdnorm.models import NormalizationChange, NormalizationReport, ValidationMessage


def report_to_dict(report: NormalizationReport) -> dict[str, object]:
    """Convert a normalization report to a JSON-serializable dictionary."""
    return {
        "input_path": report.input_path,
        "output_path": report.output_path,
        "warnings": [_validation_message_to_dict(message) for message in report.warnings],
        "errors": [_validation_message_to_dict(message) for message in report.errors],
        "changes": [_change_to_dict(change) for change in report.changes],
    }


def serialize_report(report: NormalizationReport) -> str:
    """Serialize a normalization report to formatted JSON."""
    return json.dumps(report_to_dict(report), indent=2) + "\n"


def write_report(
    path: str | Path,
    report: NormalizationReport,
    *,
    force: bool = False,
    dry_run: bool = False,
) -> None:
    """Write a normalization report as JSON."""
    write_output(path, serialize_report(report), force=force, dry_run=dry_run)


def _validation_message_to_dict(message: ValidationMessage) -> dict[str, object]:
    return {
        "level": message.level,
        "message": message.message,
        "line_number": message.line_number,
    }


def _change_to_dict(change: NormalizationChange) -> dict[str, object]:
    return {
        "line_number": change.line_number,
        "rule": change.rule,
        "description": change.description,
        "before": change.before,
        "after": change.after,
    }
