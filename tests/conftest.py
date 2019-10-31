import logging

import pytest

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__file__)


@pytest.fixture
def make_project():
    def _make_dir(root, files, dirs):
        for d, subdir in dirs.items():
            (root / d).mkdir()
            _make_dir((root / d), subdir.get("files", {}), subdir.get("dirs", {}))

        for f, contents in files.items():
            with (root / f).open("w+") as fd:
                fd.write(contents)

    def _make_project(root, to_create):
        _make_dir(root, to_create["files"], to_create["dirs"])

    return _make_project
