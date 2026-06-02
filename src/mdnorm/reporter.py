# ============================================================
# FILE:          reporter.py
# PROJECT:       MD Normalizer
# BRIEF:         Serializes normalization and check reports to JSON and writes report files.
# DOCUMENT:      docs/tool_framework.md; README.md
# REQUIREMENTS:  support-only; no formal requirement IDs assigned for v0.2.0
# COPYRIGHT:     Copyright (c) 2026 BelTech Systems LLC.
# LICENSE:       MIT License; see LICENSE in repository root.
# CLASSIFICATION: OPEN-SOURCE
# STANDARD:      Python 3.11+
# FUNCTIONS:
#   write_report(path, report, force, dry_run)
#     Writes a JSON normalization report to disk.
#   write_check_report(path, report, force, dry_run)
#     Writes a JSON advisory check report to disk.
# DEPENDENCIES:
#   Standard library: json, pathlib
#   Third-party:      none
#   Internal:         mdnorm.io, mdnorm.models
# PORTABILITY:    Supports Python 3.11 or later on Windows, Linux, and macOS.
# IMPL. STATUS:   IN_REVIEW
# HISTORY:
#   2026-05-25  Cursor    [DOCS] Replaced minimal SPDX header with STD-006 style metadata header
#   2026-06-02  Cursor    [FEAT] Added check report serialization (write_check_report) for v0.2.0
# ============================================================

"""Normalization and advisory check report generation.

Handles JSON serialisation for both ``NormalizationReport`` (produced by the
``normalize`` command) and ``CheckReport`` (produced by the ``check`` command).

The file header above is the authoritative engineering metadata source for
this module.
"""

from __future__ import annotations

import json
from pathlib import Path

from mdnorm.io import write_output
from mdnorm.models import (
    CheckFinding,
    CheckReport,
    NormalizationChange,
    NormalizationReport,
    ValidationMessage,
)


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


# ---------------------------------------------------------------------------
# Check report serialization
# ---------------------------------------------------------------------------

def check_report_to_dict(report: CheckReport) -> dict[str, object]:
    """Convert a CheckReport to a JSON-serializable dictionary."""
    warning_count = sum(1 for f in report.findings if f.level == "WARNING")
    info_count = sum(1 for f in report.findings if f.level == "INFO")
    # ok is True unless strict mode is active and warnings are present.
    ok = (warning_count == 0) if report.strict else True
    return {
        "tool": report.tool,
        "tool_version": report.tool_version,
        "command": "check",
        "input_path": report.input_path,
        "summary": {
            "info_count": info_count,
            "warning_count": warning_count,
            "strict": report.strict,
            "ok": ok,
        },
        "findings": [_finding_to_dict(f) for f in report.findings],
    }


def serialize_check_report(report: CheckReport) -> str:
    """Serialize a CheckReport to formatted JSON."""
    return json.dumps(check_report_to_dict(report), indent=2) + "\n"


def write_check_report(
    path: str | Path,
    report: CheckReport,
    *,
    force: bool = False,
    dry_run: bool = False,
) -> None:
    """Write a check report as JSON."""
    write_output(path, serialize_check_report(report), force=force, dry_run=dry_run)


def _finding_to_dict(finding: CheckFinding) -> dict[str, object]:
    return {
        "rule_id": finding.rule_id,
        "level": finding.level,
        "line_number": finding.line_number,
        "message": finding.message,
        "details": finding.details,
    }
