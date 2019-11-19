import logging
from base64 import b64decode
from pathlib import Path

from github import Github

logger = logging.getLogger("dirschema")


def _check_file(schema, filename, contents):
    if schema.get("absent"):
        return [f"{filename} shouldn't exist"]

    errors = []

    for required in schema.get("contains", []):
        if required not in contents:
            errors.append(f"{filename} is missing required string: '{required}'")

    return errors


def _check_dir(schema, dirname, found_files, found_dirs):
    if schema.get("absent"):
        return [f"{dirname} shouldn't exist"]

    allow_extra_files = schema.get("allow_extra_files")
    allow_extra_dirs = schema.get("allow_extra_dirs")
    expected_files = set(
        [f for f in schema.get("files", []) if not schema["files"][f].get("absent")]
    )
    expected_dirs = set([d for d in schema.get("dirs", []) if not schema["dirs"][d].get("absent")])
    errors = []

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

    return errors


def _check_ondisk_file(schema, file_):
    if not schema.get("contains") and not schema.get("absent"):
        return []

    contents = open(file_).read()
    return _check_file(schema, file_.name, contents)


def _check_ondisk_dir(schema, dir_, dirname=None):
    if not dirname:
        dirname = dir_.name

    found_files = set()
    found_dirs = set()
    errors = []

    for i in dir_.iterdir():
        if i.is_file():
            found_files.add(i.name)
        if i.is_dir():
            found_dirs.add(i.name)

    errors.extend(_check_dir(schema, dirname, found_files, found_dirs))

    for d in found_dirs:
        if d in schema.get("dirs", {}):
            errors.extend(_check_ondisk_dir(schema["dirs"][d], dir_ / d))

    for f in found_files:
        if f in schema.get("files", {}):
            errors.extend(_check_ondisk_file(schema["files"][f], dir_ / f))

    return errors


def _check_github_file(schema, repo, ref, file_):
    logger.debug(f"Verifying file: {file_}")

    if not schema.get("contains"):
        logger.debug(f"Schema has no content requirements, not downloading file")
        return []

    # TODO: Can we avoid assuming UTF-8 here?
    contents = b64decode(repo.get_contents(file_, ref=ref).content).decode("utf-8")
    logger.debug(f"Got contents:")
    logger.debug(contents)
    return _check_file(schema, file_, contents)


def _check_github_dir(schema, repo, ref, dir_, dirname=None):
    if not dirname:
        dirname = dir_

    found_files = set()
    found_dirs = set()
    errors = []

    logger.debug(f"Processing dir: {dirname}")
    for i in repo.get_contents(dir_, ref=ref):
        if i.type == "file":
            logger.debug(f"Found file: {i.name}")
            found_files.add(i.name)
        elif i.type == "dir":
            logger.debug(f"Found dir: {i.name}")
            found_dirs.add(i.name)

    errors.extend(_check_dir(schema, dirname, found_files, found_dirs))

    for d in found_dirs:
        if d in schema.get("dirs", {}):
            errors.extend(_check_github_dir(schema["dirs"][d], repo, ref, f"{dir_}/{d}"))

    for f in found_files:
        if f in schema.get("files", {}):
            errors.extend(_check_github_file(schema["files"][f], repo, ref, f"{dir_}/{f}"))

    return errors


def check_ondisk_structure(schema, rootdir):
    rootdir = Path(rootdir)

    if not rootdir.is_dir():
        return [f"invalid directory: {rootdir.name}"]

    return _check_ondisk_dir(schema, rootdir, "root directory")


def check_github_structure(schema, repo_name, access_token, dir_="", ref="master"):
    # TODO: error handling
    g = Github(access_token)
    repo = g.get_repo(repo_name)

    return _check_github_dir(schema, repo, ref, dir_, "root directory")


def error_report(failures):
    report = ""
    for project, errors in sorted(failures.items(), key=lambda i: i):
        report += f"{project} has errors:\n"
        for e in errors:
            report += f"* {e}\n"
        report += "\n"

    return report
