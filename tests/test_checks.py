from tempfile import TemporaryDirectory

import pytest

from mozrelenglint.checks import check_structure

from .conftest import ALL_DIRS, ALL_FILES


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
def test_check_structure(make_relengproject, tmp_path, files, dirs, expected):
    make_relengproject(tmp_path, files, dirs)
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
