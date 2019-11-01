import logging
import logging.config
import sys
from urllib.parse import urlparse

import click


@click.command()
@click.argument("schema")
@click.argument("project_dir_or_repo")
@click.option("-v", "--verbose", is_flag=True, help="Enables verbose mode")
@click.option("--access-token", help="Github access token, if checking a repository")
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

    # Surely this assumption will never break...
    if "://" in project_dir_or_repo:
        repo = urlparse(project_dir_or_repo).path[1:]
        errors = check_github_structure(schema, repo, access_token)
    else:
        errors = check_ondisk_structure(schema, project_dir_or_repo)

    if errors:
        click.echo("\n".join(errors))
        sys.exit(1)
