from pathlib import Path

import tomli

from daglib import __version__


def test_version():
    """Assert that the library's __version__ metadata stays in sync with version in pyproject.toml file"""
    try:
        pyproject_toml = next(Path.cwd().parent.glob("pyproject.toml"))
    except StopIteration:
        pyproject_toml = next(Path.cwd().glob("pyproject.toml"))
    with open(pyproject_toml, "rb") as fp:
        tool_table = tomli.load(fp).get("tool", {})
        poetry = tool_table.get("poetry", {})
        version = poetry.get("version", "FAIL")

    assert __version__ == version
