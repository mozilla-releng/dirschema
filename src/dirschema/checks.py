import logging
from pathlib import Path

logger = logging.getLogger(__file__)


def check_file(schema, file_):
    if not schema.get("contains"):
        return []

    errors = []
    contents = open(file_).read()

    for required in schema.get("contains", []):
        if required not in contents:
            errors.append(f"{file_.name} is missing required string: '{required}'")

    return errors


def check_dir(schema, dir_, dirname=None):
    if not dirname:
        dirname = dir_.name
    allow_extra_files = schema.get("allow_extra_files")
    allow_extra_dirs = schema.get("allow_extra_dirs")
    expected_files = set(schema.get("files", []))
    expected_dirs = set(schema.get("dirs", []))
    found_files = set()
    found_dirs = set()
    errors = []

    for i in dir_.iterdir():
        if i.is_file():
            found_files.add(i.name)
        if i.is_dir():
            found_dirs.add(i.name)

    # Missing files & dirs
    for f in expected_files - found_files:
        errors.append(f"missing file in {dirname}: {f}")
    for d in expected_dirs - found_dirs:
        errors.append(f"missing dir in {dirname}: {d}")

    if not allow_extra_files:
        for f in found_files - expected_files:
            errors.append(f"extra file in {dirname}: {f}")
    if not allow_extra_dirs:
        for d in found_dirs - expected_dirs:
            errors.append(f"extra dir in {dirname}: {d}")

    for d in found_dirs:
        if d in schema.get("dirs", {}):
            errors.extend(check_dir(schema["dirs"][d], dir_ / d))

    for f in found_files:
        if f in schema.get("files", {}):
            errors.extend(check_file(schema["files"][f], dir_ / f))

    return errors


def check_structure(schema, rootdir):
    rootdir = Path(rootdir)

    if not rootdir.is_dir():
        return [f"invalid directory: {rootdir.name}"]

    return check_dir(schema, rootdir, "root directory")
