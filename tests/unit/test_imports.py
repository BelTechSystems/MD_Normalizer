"""Package import smoke tests."""

import mdnorm
from mdnorm import cli, io, models, normalizer, parser, reporter, validator


def test_package_imports() -> None:
    assert mdnorm.__version__ == "0.1.0"


def test_submodules_import() -> None:
    for module in (cli, io, models, normalizer, parser, reporter, validator):
        assert module.__doc__ is not None
