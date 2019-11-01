from copy import deepcopy
from pathlib import Path
from traceback import print_exception

from click.testing import CliRunner

from dirschema.cli import dirschema

SCHEMA_PATH = Path(__file__).parent / "on-disk-schema.json"
GOOD_PROJECT = {"files": {"foo": "", "bar": ""}, "dirs": {"dir1": {"files": {"f1": "", "f2": ""}}}}
BAD_PROJECT = deepcopy(GOOD_PROJECT)
BAD_PROJECT["files"] = {}


def test_cli_good_project(make_project, tmp_path):
    make_project(tmp_path, GOOD_PROJECT)

    runner = CliRunner()
    result = runner.invoke(dirschema, [str(SCHEMA_PATH), str(tmp_path)])

    if result.exit_code != 0:
        assert False, print_exception(*result.exc_info[:3])


def test_cli_bad_project(make_project, tmp_path):
    make_project(tmp_path, BAD_PROJECT)

    runner = CliRunner()
    result = runner.invoke(dirschema, [str(SCHEMA_PATH), str(tmp_path)])

    if result.exit_code != 1:
        assert False, print_exception(*result.exc_info[:3])
