import sys

import click

from .checks import check_structure
from .schema import load_schema


@click.command()
@click.argument("schema")
@click.argument("project_dir")
def dirschema(schema, project_dir):
    schema = load_schema(open(schema).read())
    errors = check_structure(schema, project_dir)

    if errors:
        click.echo("\n".join(errors))
        sys.exit(1)
