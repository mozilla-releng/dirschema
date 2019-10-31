import logging
from os import walk
from os.path import abspath, basename, isdir

logger = logging.getLogger(__file__)

REQUIRED_FILES = {
    ".": {
        "CODE_OF_CONDUCT.md",
        "HISTORY.rst",
        "MANIFEST.in",
        "README.rst",
        "Dockerfile.test",
        "pyproject.toml",
        "setup.py",
        "tox.ini",
        ".pyup.yml",
        ".taskcluster.yml",
    },
    "requirements": {"base.in", "base.txt", "test.in", "test.txt", "local.in", "local.txt"},
    "src": set(),
    "tests": set(),
}


def check_structure(rootdir):
    rootdir = abspath(rootdir)

    errors = []

    if not isdir(rootdir):
        errors.append(f"invalid directory: {rootdir}")

    for root, dirs, files in walk(rootdir):
        dirkey = basename(root)
        root = abspath(root)
        if root != rootdir and dirkey not in REQUIRED_FILES:
            logging.debug(f"Skipping unknown dir {dirkey}")
            continue

        if root == rootdir:
            dirkey = "."
            dirs = set(dirs)

            missing_dirs = REQUIRED_FILES.keys() - dirs - {"."}
            if missing_dirs:
                errors.append(f"missing dir(s): {missing_dirs}")
            extra_dirs = dirs - REQUIRED_FILES.keys()
            if extra_dirs:
                errors.append(f"extra dir(s): {extra_dirs}")

        files = set(files)

        missing_files = REQUIRED_FILES[dirkey] - files
        logger.debug(f"Found files: {files}")
        if missing_files:
            errors.append(f"missing file(s): {missing_files}")
        extra_files = files - REQUIRED_FILES[dirkey]
        if extra_files:
            errors.append(f"extra file(s): {extra_files}")

    return errors
