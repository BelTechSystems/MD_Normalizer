# ============================================================
# FILE:          __main__.py
# PROJECT:       MD Normalizer
# BRIEF:         Provides the module entry point for `python -m mdnorm`.
# DOCUMENT:      docs/tool_framework.md; README.md
# REQUIREMENTS:  support-only; no formal requirement IDs assigned for v0.1.0
# COPYRIGHT:     Copyright (c) 2026 BelTech Systems LLC.
# LICENSE:       MIT License; see LICENSE in repository root.
# CLASSIFICATION: OPEN-SOURCE
# STANDARD:      Python 3.11+
# FUNCTIONS:
#   main()
#     Delegates CLI execution to mdnorm.cli.
# DEPENDENCIES:
#   Standard library: none
#   Third-party:      none
#   Internal:         mdnorm.cli
# PORTABILITY:    Supports Python 3.11 or later on Windows, Linux, and macOS.
# IMPL. STATUS:   IN_REVIEW
# HISTORY:
#   2026-05-25  Cursor    [DOCS] Replaced minimal SPDX header with STD-006 style metadata header
# ============================================================

"""Enable `python -m mdnorm` as a CLI entry point.

The file header above is the authoritative engineering metadata source for
this module.
"""

from mdnorm.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
