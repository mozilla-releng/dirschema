from click.testing import CliRunner

from mozrelenglint.cli import mozrelenglint


def test_cli_good_project(make_good_relengproject, tmp_path):
    make_good_relengproject(tmp_path)

    runner = CliRunner()
    result = runner.invoke(mozrelenglint, [str(tmp_path)])

    assert result.exit_code == 0


def test_cli_bad_project(make_relengproject, tmp_path):
    make_relengproject(tmp_path, {})

    runner = CliRunner()
    result = runner.invoke(mozrelenglint, [str(tmp_path)])

    assert result.exit_code == 1
    assert "missing file" in result.output
    assert "missing dir" in result.output
