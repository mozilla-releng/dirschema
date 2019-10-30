from click.testing import CliRunner

from mozrelenglint.cli import mozrelenglint


def test_cli(make_good_relengproject, tmp_path):
    make_good_relengproject(tmp_path)

    runner = CliRunner()
    result = runner.invoke(mozrelenglint, [str(tmp_path)])

    assert result.exit_code == 0
