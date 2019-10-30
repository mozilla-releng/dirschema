from os import walk
from os.path import abspath, isdir

REQUIRED_FILES = {
    "CODE_OF_CONDUCT.md",
    "HISTORY.md",
    "MANIFEST.in",
    "README.md",
    "pyproject.toml",
    "setup.py",
    "tox.ini",
    ".pyup.yml",
    ".taskcluster.yml",
}
REQUIRED_DIRS = {"src", "tests"}


def check_structure(rootdir):
    rootdir = abspath(rootdir)

    if not isdir(rootdir):
        return False

    for root, dirs, files in walk(rootdir):
        root = abspath(root)
        # We only care about the top level
        if root != rootdir:
            continue

        dirs = set(dirs)
        files = set(files)

        missing_dirs = REQUIRED_DIRS - dirs
        extra_dirs = dirs - REQUIRED_DIRS
        missing_files = REQUIRED_FILES - files
        extra_files = files - REQUIRED_FILES

        if missing_dirs or extra_dirs or missing_files or extra_files:
            return False

        return True

    return False
