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

    assert result.stdout.count("Success!") == 1


def test_cli_bad_project(make_project, tmp_path):
    make_project(tmp_path, BAD_PROJECT)

    runner = CliRunner()
    result = runner.invoke(dirschema, [str(SCHEMA_PATH), str(tmp_path)])

    if result.exit_code != 1:
        assert False, print_exception(*result.exc_info[:3])

    assert result.stdout.count("missing file in root directory") == 2


def test_cli_multiple_good_projects(make_project, tmp_path_factory):
    dirs = [tmp_path_factory.mktemp("d1"), tmp_path_factory.mktemp("d2")]

    for d in dirs:
        make_project(d, GOOD_PROJECT)

    runner = CliRunner()
    result = runner.invoke(dirschema, [str(SCHEMA_PATH), *[str(d) for d in dirs]])

    if result.exit_code != 0:
        assert False, print_exception(*result.exc_info[:3])

    assert result.stdout.count("Success!") == 2


def test_cli_multiple_projects_one_bad(make_project, tmp_path_factory):
    good_dir, bad_dir = [tmp_path_factory.mktemp("d1"), tmp_path_factory.mktemp("d2")]

    make_project(good_dir, GOOD_PROJECT)
    make_project(bad_dir, BAD_PROJECT)

    runner = CliRunner()
    result = runner.invoke(dirschema, [str(SCHEMA_PATH), str(good_dir), str(bad_dir)])

    if result.exit_code != 1:
        assert False, print_exception(*result.exc_info[:3])

    assert result.stdout.count("Success!") == 1
    assert result.stdout.count("missing file in root directory") == 2
