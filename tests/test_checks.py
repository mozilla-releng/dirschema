from tempfile import TemporaryDirectory

import pytest

from mozrelenglint.checks import check_structure


@pytest.fixture(scope="function")
def full_structure(tmp_path):
    files = (
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
    dirs = ("src", "tests")
    for f in files:
        with open(tmp_path / f, "w+") as fd:
            # Create an empty file
            pass
    for d in dirs:
        (tmp_path / d).mkdir()

    return tmp_path


def test_structure(full_structure):
    assert check_structure(full_structure) == True
