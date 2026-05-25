# ============================================================
# FILE:          cli.py
# PROJECT:       MD Normalizer
# BRIEF:         Provides the command-line interface for normalization and validation.
# DOCUMENT:      docs/tool_framework.md; README.md; docs/decisions/DECISIONS.md
# REQUIREMENTS:  support-only; no formal requirement IDs assigned for v0.1.0
# COPYRIGHT:     Copyright (c) 2026 BelTech Systems LLC.
# LICENSE:       MIT License; see LICENSE in repository root.
# CLASSIFICATION: OPEN-SOURCE
# STANDARD:      Python 3.11+
# FUNCTIONS:
#   build_parser()
#     Builds the argparse command tree for normalize and validate.
#   run_normalize(args)
#     Executes normalization, validation, output writing, and optional report writing.
#   run_validate(args)
#     Executes validation and emits warnings or errors.
#   main(argv)
#     Parses CLI arguments and dispatches subcommands.
# DEPENDENCIES:
#   Standard library: argparse, sys
#   Third-party:      none
#   Internal:         mdnorm.io, mdnorm.normalizer, mdnorm.reporter, mdnorm.validator
# PORTABILITY:    Supports Python 3.11 or later on Windows, Linux, and macOS.
# IMPL. STATUS:   IN_REVIEW
# HISTORY:
#   2026-05-25  Cursor    [DOCS] Added STD-006 source metadata header for v0.1.0 release preparation
# ============================================================

"""Command-line interface for MD Normalizer.

The file header above is the authoritative engineering metadata source for
this module.
"""

from __future__ import annotations

import argparse
import sys

from mdnorm.io import IoError, read_input, write_output
from mdnorm.normalizer import normalize
from mdnorm.reporter import write_report
from mdnorm.validator import format_message, validate


def build_parser() -> argparse.ArgumentParser:
    """Build the top-level argument parser."""
    parser = argparse.ArgumentParser(
        prog="mdnorm",
        description=(
            "Normalize rough text or inconsistent Markdown into clean, "
            "structured Markdown."
        ),
    )
    subparsers = parser.add_subparsers(dest="command")

    normalize_parser = subparsers.add_parser(
        "normalize",
        help="Normalize a Markdown or plain-text file.",
    )
    normalize_parser.add_argument(
        "--in",
        dest="input_path",
        required=True,
        metavar="PATH",
        help="Input text or Markdown file.",
    )
    normalize_parser.add_argument(
        "--out",
        dest="output_path",
        required=True,
        metavar="PATH",
        help="Output Markdown file.",
    )
    normalize_parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite an existing output file.",
    )
    normalize_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without writing the output file.",
    )
    normalize_parser.add_argument(
        "--report",
        dest="report_path",
        metavar="PATH",
        help="Write a JSON normalization report to PATH.",
    )

    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate a Markdown file.",
    )
    validate_parser.add_argument(
        "--in",
        dest="input_path",
        required=True,
        metavar="PATH",
        help="Markdown file to validate.",
    )

    return parser


def run_normalize(args: argparse.Namespace) -> int:
    """Handle the normalize subcommand."""
    try:
        content = read_input(args.input_path)
        normalized, report = normalize(content)
        report.input_path = str(args.input_path)
        report.output_path = str(args.output_path)

        validation = validate(normalized)
        report.warnings.extend(validation.warnings)
        report.errors.extend(validation.errors)

        write_output(
            args.output_path,
            normalized,
            force=args.force,
            dry_run=args.dry_run,
        )
        if args.report_path is not None:
            write_report(
                args.report_path,
                report,
                force=args.force,
                dry_run=False,
            )
    except IoError as exc:
        print(exc, file=sys.stderr)
        return 1

    return 0


def run_validate(args: argparse.Namespace) -> int:
    """Handle the validate subcommand."""
    try:
        content = read_input(args.input_path)
    except IoError as exc:
        print(exc, file=sys.stderr)
        return 1

    result = validate(content)

    for message in result.warnings:
        print(format_message(message), file=sys.stderr)
    for message in result.errors:
        print(format_message(message), file=sys.stderr)

    if not result.ok:
        return 1

    return 0


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    if args.command == "normalize":
        return run_normalize(args)

    if args.command == "validate":
        return run_validate(args)

    parser.error(f"command {args.command!r} is not implemented yet")
    return 1


if __name__ == "__main__":
    sys.exit(main())
