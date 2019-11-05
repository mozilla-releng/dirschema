import logging
import logging.config
import os
import sys
from urllib.parse import urlparse

import click


@click.command()
@click.argument("schema")
@click.argument("project_dir_or_repo", nargs=-1)
@click.option("-v", "--verbose", is_flag=True, help="Enables verbose mode")
@click.option(
    "--access-token",
    default=os.environ.get("GITHUB_ACCESS_TOKEN"),
    help="Github access token, if checking a repository",
)
def dirschema(schema, project_dir_or_repo, verbose, access_token):
    # TODO: why isn't logging.config.dictConfig working when we
    # set config for a "dirschema" logger
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
        logging.getLogger("github").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)
    else:
        logging.basicConfig(level=logging.WARNING)

    from .checks import check_github_structure, check_ondisk_structure
    from .schema import load_schema

    schema = load_schema(open(schema).read())

    project_errors = {}

    for tocheck in project_dir_or_repo:
        print(tocheck)
        # Surely this assumption will never break...
        if "://" in tocheck:
            repo = urlparse(tocheck).path[1:]
            project_errors[tocheck] = check_github_structure(schema, repo, access_token)
        else:
            project_errors[tocheck] = check_ondisk_structure(schema, tocheck)

    any_errors = False
    for project, errors in project_errors.items():
        if errors:
            any_errors = True
            click.echo(f"{project}: Has errors")
            click.echo("\n".join(errors))
        else:
            click.echo(f"{project}: Success!")

    if any_errors:
        sys.exit(1)
    else:
        sys.exit(0)
