# ============================================================
# FILE:          release_check.ps1
# PROJECT:       MD Normalizer
# BRIEF:         Repeatable release verification script for MD Normalizer.
# DOCUMENT:      docs/release_testing.md
# REQUIREMENTS:  support-only; no formal requirement IDs assigned for v0.2.1
# COPYRIGHT:     Copyright (c) 2026 BelTech Systems LLC.
# LICENSE:       MIT License; see LICENSE in repository root.
# CLASSIFICATION: OPEN-SOURCE
# STANDARD:      PowerShell 5.1+ / PowerShell 7+
# DEPENDENCIES:
#   Tools:         python, pytest, mdnorm module invocation
#   Repository:    examples/rough_ai_output.md, README.md, CHANGELOG.md,
#                  docs/decisions/DECISIONS.md
# PORTABILITY:    Intended for Windows PowerShell or PowerShell Core from
#                 repository root with an active virtual environment.
# IMPL. STATUS:  IN_REVIEW
# HISTORY:
#   2026-06-02  Cursor    [FEAT] Created for v0.2.1 hardening release verification
#   2026-06-02  Cursor    [FIX]  Replaced Unicode separator comments with plain ASCII
# ============================================================

<#
.SYNOPSIS
    Repeatable release verification script for MD Normalizer.

.DESCRIPTION
    Runs the full suite of release-acceptance checks from the repository root.
    Verifies the test suite, all CLI commands, output file creation, overwrite
    protection, document-quality checks on project documents, and JSON report
    generation.  Prints a PASS/FAIL summary for every step and exits non-zero
    if any step fails.

.NOTES
    Run from the repository root with an active virtual environment:

      powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\release_check.ps1

    See docs/release_testing.md for full setup instructions.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Continue"

# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

$Failures = 0

function Confirm-Step {
    param([string]$Label)
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  [FAIL] $Label  (exit $LASTEXITCODE)" -ForegroundColor Red
        $script:Failures++
    } else {
        Write-Host "  [PASS] $Label" -ForegroundColor Green
    }
}

function Confirm-StepShouldFail {
    param([string]$Label)
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [FAIL] $Label  (expected non-zero exit, got 0)" -ForegroundColor Red
        $script:Failures++
    } else {
        Write-Host "  [PASS] $Label  (correctly rejected, exit $LASTEXITCODE)" -ForegroundColor Green
    }
}

function Confirm-FileExists {
    param([string]$Path)
    if (Test-Path $Path) {
        Write-Host "  [PASS] File exists: $Path" -ForegroundColor Green
    } else {
        Write-Host "  [FAIL] Expected file not found: $Path" -ForegroundColor Red
        $script:Failures++
    }
}

# ------------------------------------------------------------
# Setup
# ------------------------------------------------------------

Write-Host ""
Write-Host "MD Normalizer Release Check" -ForegroundColor Cyan
Write-Host "============================" -ForegroundColor Cyan
Write-Host "  Working directory : $(Get-Location)"
Write-Host "  Python            : $(python --version 2>&1)"
Write-Host ""

if (-not (Test-Path "output")) {
    New-Item -ItemType Directory -Path "output" | Out-Null
    Write-Host "  Created output/ directory"
}

# ------------------------------------------------------------
# Step 1: Automated test suite
# ------------------------------------------------------------

Write-Host ""
Write-Host "Step 1: Automated tests" -ForegroundColor Cyan
Write-Host "----------------------------------------------------------------------"
python -m pytest -q
Confirm-Step "pytest -q"

# ------------------------------------------------------------
# Step 2: CLI help
# ------------------------------------------------------------

Write-Host ""
Write-Host "Step 2: CLI help" -ForegroundColor Cyan
Write-Host "----------------------------------------------------------------------"
python -m mdnorm --help | Out-Null
Confirm-Step "mdnorm --help"

# ------------------------------------------------------------
# Step 3: Normalize with report
# ------------------------------------------------------------

Write-Host ""
Write-Host "Step 3: Normalize with report" -ForegroundColor Cyan
Write-Host "----------------------------------------------------------------------"
python -m mdnorm normalize `
    --in examples/rough_ai_output.md `
    --out output/clean.md `
    --force `
    --report output/normalization_report.json
Confirm-Step "normalize --force --report"
Confirm-FileExists "output/clean.md"
Confirm-FileExists "output/normalization_report.json"

# ------------------------------------------------------------
# Step 4: Overwrite protection
# ------------------------------------------------------------

Write-Host ""
Write-Host "Step 4: Overwrite protection" -ForegroundColor Cyan
Write-Host "----------------------------------------------------------------------"
# output/clean.md exists from step 3; normalize without --force must be rejected.
python -m mdnorm normalize `
    --in examples/rough_ai_output.md `
    --out output/clean.md
Confirm-StepShouldFail "normalize without --force (must reject existing output)"

# ------------------------------------------------------------
# Step 5: Validate
# ------------------------------------------------------------

Write-Host ""
Write-Host "Step 5: Validate normalized output" -ForegroundColor Cyan
Write-Host "----------------------------------------------------------------------"
python -m mdnorm validate --in output/clean.md
Confirm-Step "validate output/clean.md"

# ------------------------------------------------------------
# Step 6: Document quality checks on project documents
# ------------------------------------------------------------

Write-Host ""
Write-Host "Step 6: Check project documents (--strict)" -ForegroundColor Cyan
Write-Host "----------------------------------------------------------------------"

python -m mdnorm check --in README.md --strict
Confirm-Step "check README.md --strict"

python -m mdnorm check --in CHANGELOG.md --strict
Confirm-Step "check CHANGELOG.md --strict"

python -m mdnorm check --in docs/decisions/DECISIONS.md --strict
Confirm-Step "check docs/decisions/DECISIONS.md --strict"

# ------------------------------------------------------------
# Step 7: Check with JSON report
# ------------------------------------------------------------

Write-Host ""
Write-Host "Step 7: Check with JSON report" -ForegroundColor Cyan
Write-Host "----------------------------------------------------------------------"
python -m mdnorm check `
    --in README.md `
    --report output/check_report.json `
    --force
Confirm-Step "check README.md --report --force"
Confirm-FileExists "output/check_report.json"

# ------------------------------------------------------------
# Summary
# ------------------------------------------------------------

Write-Host ""
Write-Host "============================" -ForegroundColor Cyan
if ($Failures -gt 0) {
    Write-Host "Release check FAILED: $Failures step(s) did not pass." -ForegroundColor Red
    exit 1
} else {
    Write-Host "Release check PASSED: all steps succeeded." -ForegroundColor Green
    exit 0
}
