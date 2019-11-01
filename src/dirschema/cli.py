import sys

import click

from .checks import check_github_structure, check_ondisk_structure
from .schema import load_schema


@click.command()
@click.argument("schema")
@click.argument("project_dir_or_repo")
def dirschema(schema, project_dir_or_repo):
    schema = load_schema(open(schema).read())

    # Surely this assumption will never break...
    if "://" in project_dir_or_repo:
        errors = check_github_structure(schema, project_dir_or_repo)
    else:
        errors = check_ondisk_structure(schema, project_dir_or_repo)

    if errors:
        click.echo("\n".join(errors))
        sys.exit(1)
