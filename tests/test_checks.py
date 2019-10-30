from tempfile import TemporaryDirectory

import pytest

from mozrelenglint.checks import check_structure

ALL_FILES = (
    "CODE_OF_CONDUCT.md",
    "HISTORY.md",
    "MANIFEST.in",
    "README.md",
    "pyproject.toml",
    "setup.py",
    "tox.ini",
    ".pyup.yml",
    ".taskcluster.yml",
)
ALL_DIRS = ("src", "tests")


@pytest.mark.parametrize(
    "files,dirs,expected",
    (
        (ALL_FILES, ALL_DIRS, []),
        (ALL_FILES[:-2], ALL_DIRS, ["missing file(s)"]),
        (ALL_FILES, ALL_DIRS[:1], ["missing dir(s)"]),
        (ALL_FILES + ("foo",), ALL_DIRS, ["extra file(s)"]),
        (ALL_FILES, ALL_DIRS + ("foo",), ["extra dir(s)"]),
        (
            ALL_FILES[:-2] + ("foo",),
            ALL_DIRS[:1] + ("bar",),
            ["missing file(s)", "missing dir(s)", "extra file(s)", "extra dir(s)"],
        ),
    ),
)
def test_check_structure(tmp_path, files, dirs, expected):
    for f in files:
        with open(tmp_path / f, "w+") as fd:
            # Create an empty file
            pass
    for d in dirs:
        (tmp_path / d).mkdir()

    result = check_structure(tmp_path)

    if len(expected) == 0:
        if len(result) != 0:
            assert False, f"Expected 0 errors but got: {result}"
    else:
        for err in expected:
            if not any([err in r for r in result]):
                assert False, f"Expected to find '{err}' in '{result}'"


def test_check_structure_invalid_dir():
    result = check_structure("/squigglyborf")
    assert len(result) == 1
    assert "invalid directory" in result[0]
