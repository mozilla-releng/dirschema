import sys

import click

from .checks import check_structure


@click.command()
@click.argument("project_dir")
def dirschema(project_dir):
    errors = check_structure(project_dir)

    if errors:
        click.echo("\n".join(errors))
        sys.exit(1)
