from copy import deepcopy
from tempfile import TemporaryDirectory

import pytest

from mozrelenglint.checks import check_structure

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


@pytest.mark.parametrize(
    "files,expected",
    (
        (GOOD_PROJECT, []),
        # TODO: more tests here!
    ),
)
def test_check_structure(make_project, tmp_path, files, expected):
    make_project(tmp_path, files)
    import os

    for root, dirs2, files2 in os.walk(tmp_path):
        print(root)
        print(dirs2)
        print(files2)
    result = check_structure(TEST_SCHEMA, tmp_path)

    if len(expected) == 0:
        if len(result) != 0:
            assert False, f"Expected 0 errors but got: {result}"
    else:
        for err in expected:
            if not any([err in r for r in result]):
                assert False, f"Expected to find '{err}' in '{result}'"


def test_check_structure_invalid_dir():
    result = check_structure(TEST_SCHEMA, "/squigglyborf")
    assert len(result) == 1
    assert "invalid directory" in result[0]
