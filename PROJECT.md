# MD Normalizer Tool Framework Project

## 1. Tool Identity

### Tool Name
Markdown Normalizer

### Short Description
A structure-aware command line tool that converts rough text, copied AI output, or inconsistent Markdown into clean, predictable, template-aligned Markdown documents.

### Problem Statement
Users often receive or draft text that looks like Markdown but lacks consistent structure, heading levels, spacing, list formatting, code block handling, or required document sections. This creates friction when the content needs to be saved, version-controlled, reused, or processed by downstream tools.

### Primary Goal
Normalize rough text or inconsistent Markdown into clean, valid, structured Markdown while preserving the user’s intended content.

### Success Criteria
- Produces clean Markdown from rough text or inconsistent Markdown
- Preserves meaning and user-authored content
- Enforces optional document templates
- Supports repeatable formatting rules
- Allows human review and editing
- Works without requiring AI for basic normalization

---

## 2. Intended Users

### Target Users
- Engineers
- Technical writers
- Developers
- Documentation maintainers
- Users working with AI-generated content

### User Skill Level
- Beginner to advanced

### Primary Use Cases
- Clean AI-generated Markdown output
- Convert rough notes into structured Markdown
- Enforce project document templates
- Normalize headings, lists, spacing, and code blocks
- Prepare Markdown for version control or downstream processing

### Out-of-Scope Use Cases
- Full semantic rewriting
- Replacing technical editing
- Automatic document authorship from no input
- Complex publishing workflows such as PDF or DOCX generation

---

## 3. Operating Principles

- Preserve user intent
- Prefer deterministic formatting rules
- Avoid unnecessary rewriting
- Keep output human-readable
- Make structural changes explicit
- Support templates without requiring them
- Allow human review before overwrite
- Treat Markdown as an editable engineering artifact

---

## 4. Inputs and Outputs

### Primary Inputs
- Plain text file
- Markdown file
- Copied AI response saved as text
- Optional template definition

### Primary Outputs
- Normalized Markdown file
- Optional report of changes
- Optional validation result

### Intermediate Artifacts
- Parsed document structure
- Section map
- Normalization report

### Final Deliverables
- Clean `.md` file
- Optional `.json` or `.yaml` report

---

## 5. Pipeline Overview

```text
draft.txt / rough.md
   ↓ parse
document_structure
   ↓ normalize
normalized_structure
   ↓ validate
validation_report
   ↓ write
clean.md
6. Pipeline Stages
6.1 parse

Purpose:
Read rough text or Markdown and identify document structure.

Input:
draft.txt or rough.md

Output:
Internal document structure

Responsibilities:

Detect headings
Detect bullet lists
Detect numbered lists
Detect code blocks
Detect tables where possible
Preserve paragraphs
Identify malformed Markdown patterns

Validation:

Input file exists
Input file is readable
File is not empty
6.2 normalize

Purpose:
Apply deterministic formatting rules to produce clean Markdown.

Input:
Parsed document structure

Output:
Normalized document structure

Responsibilities:

Normalize heading levels
Normalize blank lines
Normalize bullet markers
Normalize numbered lists
Normalize fenced code blocks
Remove trailing whitespace
Preserve code block contents
Preserve meaningful user text

Validation:

No malformed heading hierarchy
No unclosed code fences
No broken list nesting
6.3 structure

Purpose:
Optionally align the document to a known template.

Input:
Normalized document structure and optional template

Output:
Template-aligned Markdown structure

Responsibilities:

Insert missing required sections
Reorder known sections if configured
Preserve unknown sections
Add placeholder text where required
Report missing or inferred content

Validation:

Required sections present
Template rules satisfied
Unknown content preserved
6.4 validate

Purpose:
Check that the normalized Markdown meets formatting and template requirements.

Input:
Normalized Markdown structure

Output:
Validation report

Responsibilities:

Check required headings
Check heading order
Check list consistency
Check code fence closure
Check line length if configured
Check front matter if configured

Validation:

Pass/fail result
Warning list
Error list
6.5 write

Purpose:
Write the final normalized Markdown file.

Input:
Validated Markdown structure

Output:
clean.md

Responsibilities:

Write output file
Preserve original file unless --force is used
Optionally write report file
Optionally create backup

Validation:

Output path is writable
Existing file handling follows overwrite policy
7. Artifact Contracts
7.1 Input Text or Markdown

Accepted Formats:

.txt
.md

Required Content:

At least one paragraph, heading, list, or code block

Optional Content:

Existing Markdown headings
Lists
Tables
Code blocks
Front matter

Validation Rules:

File must be readable
File must not be empty
Encoding should be UTF-8
7.2 Normalized Markdown

Format:
Markdown

Required Content:

Valid heading structure if headings are present
Clean spacing between sections
Consistent list formatting
Closed code fences

Optional Content:

YAML front matter
Tables
Links
Images
Template placeholders

Validation Rules:

No unclosed fenced code blocks
No malformed headings
No accidental heading jumps unless allowed
No trailing whitespace
7.3 Template Definition

Format:
YAML or Markdown-based template

Required Content:

Template name
Required sections
Optional sections

Optional Content:

Heading levels
Section order
Placeholder text
Validation rules

Validation Rules:

Required sections must be uniquely named
Heading levels must be valid
Template must not define conflicting section names
7.4 Normalization Report

Format:
JSON, YAML, or Markdown

Required Content:

Input file
Output file
Rules applied
Warnings
Errors

Optional Content:

Section map
Inserted sections
Reordered sections
Preserved unknown sections
8. CLI Structure
mdnorm normalize --in draft.txt --out clean.md
mdnorm normalize --in rough.md --out clean.md --force
mdnorm validate  --in clean.md
mdnorm check     --in rough.md --template tool_framework.yaml
mdnorm template  --name tool-framework --out tool_framework.md

Alternative project-integrated form:

archforge normalize --in draft.txt --out clean.md
archforge normalize --in rough.md --out docs/tool_framework.md --template tool-framework
9. Human Review and Edit Policy
The tool shall not overwrite existing files unless --force is used.
The tool shall preserve unknown content unless explicitly configured otherwise.
The tool shall report inserted, moved, or normalized sections.
The tool shall allow users to edit normalized Markdown manually.
Manual edits shall be treated as authoritative input on the next run.
The tool shall support a dry-run mode.

Example:

mdnorm normalize --in draft.txt --out clean.md --dry-run
10. Validation Strategy
Formatting Validation
Heading levels are valid
Lists use consistent bullet markers
Numbered lists are normalized
Code fences are closed
Blank lines are consistent
Trailing whitespace is removed
Template Validation
Required sections exist
Required section order is satisfied
Placeholder sections are marked clearly
Unknown sections are allowed or reported based on configuration
Safety Validation
Existing output file is not overwritten without permission
Code block contents are not reformatted unless explicitly requested
User content is preserved
11. Traceability Model
rough text
   ↓
parsed block
   ↓
normalized block
   ↓
template section
   ↓
final Markdown

Each change should be explainable in the normalization report.

Example:

Line 12: converted "Tool Name:" to "## Tool Name"
Line 18: normalized "*" bullet to "-"
Line 31: inserted missing "Open Questions" section
12. Project Folder Layout
project/
  docs/
    tool_framework.md
    decisions.md

  examples/
    rough_tool_notes.txt
    rough_ai_output.md

  templates/
    tool_framework.yaml
    decision_record.yaml

  output/
    clean.md
    normalization_report.json
13. Configuration and Defaults
Default Rules
Use # style headings
Use - for unordered lists
Use fenced code blocks with triple backticks
Preserve code block contents
Use one blank line between paragraphs
Use one blank line before and after headings
Remove trailing whitespace
Config File

Optional project configuration file:

normalizer:
  heading_style: atx
  bullet_marker: "-"
  preserve_unknown_sections: true
  overwrite_policy: require_force
  code_blocks:
    preserve_contents: true
  templates:
    default: tool_framework
Output Naming Rules

Default output may be inferred as:

input:  draft.txt
output: draft.normalized.md
14. Error Handling and Recovery
Input Is Incomplete
Report missing structure
Produce best-effort Markdown if possible
Mark missing required sections if template is used
Markdown Is Malformed
Attempt safe repair
Report repair actions
Stop only on ambiguous or destructive changes
Template Validation Fails
Insert missing sections if configured
Otherwise report errors and stop
Output File Exists
Stop unless --force is used
Optionally create .bak backup
AI Output Contains Non-Markdown Text
Strip conversational framing if configured
Preserve main content
Report removed wrapper text
15. Non-Goals
The tool shall not replace a technical editor.
The tool shall not invent technical content unless AI-assisted mode is explicitly enabled.
The tool shall not generate full documents from empty input.
The tool shall not reformat source code inside fenced code blocks by default.
The tool shall not convert Markdown to PDF, DOCX, or HTML in the baseline version.
16. Example Workflow
Example Input
Tool Name:
Markdown Normalizer

Problem:
AI output often looks like markdown but is not consistently formatted.

Users:
engineers
technical writers
developers

Workflow:
parse
normalize
validate
write
Expected Output
# Markdown Normalizer

## Problem

AI output often looks like Markdown but is not consistently formatted.

## Users

- Engineers
- Technical writers
- Developers

## Workflow

1. Parse
2. Normalize
3. Validate
4. Write
17. Current State
Concept defined
Primary use case identified
CLI structure proposed
Deterministic baseline preferred
AI-assisted mode optional for later versions
18. Roadmap
Short-Term
Implement deterministic Markdown cleanup
Add CLI command
Support dry-run mode
Add basic validation report
Medium-Term
Add template enforcement
Add configurable rules
Add section insertion
Add project-level config file
Long-Term
Add optional AI-assisted structuring
Add semantic section inference
Add traceability reports
Integrate with larger document pipelines
19. Open Questions
Should this be a standalone tool or an ArchForge utility command?
Should template definitions be YAML, Markdown, or both?
Should the tool remove conversational AI framing automatically?
Should section reordering be automatic or only reported?
Should AI-assisted mode be included in version 1 or deferred?
20. Related Decisions
D-001: Adopt Tool Framework Reference Document
D-002: Adopt Structure-Aware Markdown Normalization
D-003: Preserve User Content During Normalization
D-004: Use Deterministic Rules Before AI Assistance