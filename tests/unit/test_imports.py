"""Package import smoke tests."""

import mdnorm
from mdnorm import checker, cli, io, models, normalizer, parser, reporter, validator


def test_package_imports() -> None:
    assert mdnorm.__version__ == "0.2.1"


def test_submodules_import() -> None:
    for module in (checker, cli, io, models, normalizer, parser, reporter, validator):
        assert module.__doc__ is not None
