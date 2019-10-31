import logging

import pytest

from mozrelenglint.checks import REQUIRED_FILES

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__file__)


@pytest.fixture
def make_relengproject():
    def _make_releng_project(tmp, required_files):
        for d, files in required_files.items():
            logger.debug(tmp / d)
            if d != ".":
                (tmp / d).mkdir()
            for f in files:
                logger.debug(tmp / d / f)
                with (tmp / d / f).open("w+"):
                    # Create an empty file
                    pass

    return _make_releng_project


@pytest.fixture
def make_good_relengproject(make_relengproject):
    def _make_good_releng_project(tmp):
        return make_relengproject(tmp, REQUIRED_FILES)

    return _make_good_releng_project
