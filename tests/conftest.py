import pytest

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


@pytest.fixture
def make_relengproject():
    def _make_releng_project(tmp, files, dirs):
        for f in files:
            with open(tmp / f, "w+") as fd:
                # Create an empty file
                pass
        for d in dirs:
            (tmp / d).mkdir()

    return _make_releng_project
