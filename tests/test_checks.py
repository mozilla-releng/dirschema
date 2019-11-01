from copy import deepcopy

import pytest

from dirschema.checks import check_ondisk_structure

TEST_SCHEMA = {
    "files": {"foo": {}, "bar": {"contains": ["bar1"]}, "baz": {"contains": ["bugs", "babs"]}},
    "dirs": {
        "dir1": {
            "allow_extra_files": False,
            "allow_extra_dirs": False,
            "files": {"f1": {}},
            "dirs": {
                "nested1": {
                    "allow_extra_files": False,
                    "allow_extra_dirs": False,
                    "files": {"nested-f1": {}},
                }
            },
        },
        "dir2": {
            "allow_extra_files": True,
            "allow_extra_dirs": True,
            "files": {"required-file": {}},
        },
    },
}

GOOD_PROJECT = {
    "files": {
        "foo": "i am a foo file",
        "bar": "i contain bar1",
        "baz": """
i am a multiline file
that contains bugs
and babs
""",
    },
    "dirs": {
        "dir1": {"files": {"f1": ""}, "dirs": {"nested1": {"files": {"nested-f1": "nested file"}}}},
        "dir2": {
            "files": {"required-file": "i am required", "extra1": "", "extra2": ""},
            "dirs": {"extradir": {"files": {"superextrafile": ""}}},
        },
    },
}

WRONG_CONTENTS = deepcopy(GOOD_PROJECT)
WRONG_CONTENTS["files"]["bar"] = "wrong contents"
MISSING_FILE = deepcopy(GOOD_PROJECT)
del MISSING_FILE["files"]["foo"]
MISSING_DIR = deepcopy(GOOD_PROJECT)
del MISSING_DIR["dirs"]["dir2"]
EXTRA_FILE = deepcopy(GOOD_PROJECT)
EXTRA_FILE["files"]["extra"] = "i am an extra file"
EXTRA_DIR = deepcopy(GOOD_PROJECT)
EXTRA_DIR["dirs"]["extradir"] = {"files": {"extra": ""}}
MISSING_AND_EXTRA = deepcopy(GOOD_PROJECT)
MISSING_AND_EXTRA["files"]["baz"] = "bad string1"
del MISSING_AND_EXTRA["dirs"]["dir1"]["files"]["f1"]
del MISSING_AND_EXTRA["dirs"]["dir1"]["dirs"]["nested1"]
MISSING_AND_EXTRA["dirs"]["dir1"]["files"]["extra"] = "extra extra"
MISSING_AND_EXTRA["dirs"]["dir1"]["dirs"]["extradir"] = {"files": {"another-extra": ""}}


@pytest.mark.parametrize(
    "files,expected",
    (
        (GOOD_PROJECT, ()),
        (WRONG_CONTENTS, ("bar is missing required string",)),
        (MISSING_FILE, ("missing file in root directory: foo",)),
        (MISSING_DIR, ("missing dir in root directory: dir2",)),
        (EXTRA_FILE, ("extra file in root directory: extra",)),
        (EXTRA_DIR, ("extra dir in root directory: extradir",)),
        (
            MISSING_AND_EXTRA,
            (
                "baz is missing required string",
                "missing file in dir1: f1",
                "missing dir in dir1: nested1",
                "extra file in dir1: extra",
                "extra dir in dir1: extradir",
            ),
        ),
    ),
)
def test_check_ondisk_structure(make_project, tmp_path, files, expected):
    make_project(tmp_path, files)

    result = check_ondisk_structure(TEST_SCHEMA, tmp_path)

    if len(expected) == 0:
        if len(result) != 0:
            assert False, f"Expected 0 errors but got: {result}"
    else:
        for err in expected:
            if not any([err in r for r in result]):
                assert False, f"Expected to find '{err}' in '{result}'"


def test_check_ondisk_structure_invalid_dir():
    result = check_ondisk_structure(TEST_SCHEMA, "/squigglyborf")
    assert len(result) == 1
    assert "invalid directory" in result[0]
