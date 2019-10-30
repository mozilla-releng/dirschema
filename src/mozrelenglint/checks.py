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

    errors = []

    if not isdir(rootdir):
        errors.append(f"invalid directory: {rootdir}")

    for root, dirs, files in walk(rootdir):
        root = abspath(root)
        # We only care about the top level
        if root != rootdir:
            continue

        dirs = set(dirs)
        files = set(files)

        missing_dirs = REQUIRED_DIRS - dirs
        if missing_dirs:
            errors.append(f"missing dir(s): {missing_dirs}")
        extra_dirs = dirs - REQUIRED_DIRS
        if extra_dirs:
            errors.append(f"extra dir(s): {extra_dirs}")
        missing_files = REQUIRED_FILES - files
        if missing_files:
            errors.append(f"missing file(s): {missing_files}")
        extra_files = files - REQUIRED_FILES
        if extra_files:
            errors.append(f"extra file(s): {extra_files}")

    return errors
