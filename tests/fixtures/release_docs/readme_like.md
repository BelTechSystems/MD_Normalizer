# MD Normalizer Example

A clean README-like fixture document used for checker regression testing.

## Installation

Install in editable mode using a virtual environment:

```bash
pip install -e ".[dev]"
```

## Usage

Run the tool using the module entry point:

```bash
python -m mdnorm normalize --in input.md --out output.md
python -m mdnorm validate --in output.md
python -m mdnorm check --in output.md --strict
```

## Configuration

No project-level configuration file is required.
All behavior is controlled through CLI options.

## License

MIT License. Copyright (c) 2026 BelTech Systems LLC.
