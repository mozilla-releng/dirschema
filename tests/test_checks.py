from copy import deepcopy
from tempfile import TemporaryDirectory

import pytest

from mozrelenglint.checks import REQUIRED_FILES, check_structure

# TODO: Is there a better way to get one part of a set?
MISSING_REQUIRED_FILES = deepcopy(REQUIRED_FILES)
MISSING_REQUIRED_FILES["."] = set(list(REQUIRED_FILES["."])[:-2])
MISSING_REQUIRED_DIRS = deepcopy(REQUIRED_FILES)
del MISSING_REQUIRED_DIRS["src"]
EXTRA_REQUIRED_FILES = deepcopy(REQUIRED_FILES)
EXTRA_REQUIRED_FILES["requirements"].add("test2.in")
EXTRA_REQUIRED_DIRS = deepcopy(REQUIRED_FILES)
EXTRA_REQUIRED_DIRS["extra"] = set()
MISSING_AND_EXTRA = deepcopy(REQUIRED_FILES)
MISSING_AND_EXTRA["."] = set(list(REQUIRED_FILES["."])[:-2])
MISSING_AND_EXTRA["extra"] = set()
MISSING_AND_EXTRA["src"] = {"foo.py"}
del MISSING_AND_EXTRA["tests"]


@pytest.mark.parametrize(
    "files,expected",
    (
        (REQUIRED_FILES, []),
        (MISSING_REQUIRED_FILES, ["missing file(s)"]),
        (MISSING_REQUIRED_DIRS, ["missing dir(s)"]),
        (EXTRA_REQUIRED_FILES, ["extra file(s)"]),
        (EXTRA_REQUIRED_DIRS, ["extra dir(s)"]),
        (MISSING_AND_EXTRA, ["missing file(s)", "missing dir(s)", "extra file(s)", "extra dir(s)"]),
    ),
)
def test_check_structure(make_relengproject, tmp_path, files, expected):
    make_relengproject(tmp_path, files)
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
