import logging
import logging.config
import os
import sys
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlparse

import click


@click.group()
@click.option("-v", "--verbose", is_flag=True, help="Enables verbose mode")
@click.option(
    "--access-token",
    default=os.environ.get("GITHUB_ACCESS_TOKEN"),
    help="Github access token, if checking a repository",
)
@click.pass_context
def dirschema(ctx, verbose, access_token):
    # TODO: why isn't logging.config.dictConfig working when we
    # set config for a "dirschema" logger
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
        logging.getLogger("github").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)
    else:
        logging.basicConfig(level=logging.WARNING)

    ctx.ensure_object(dict)
    ctx.obj["access_token"] = access_token


def do_check_projects(projects, access_token):
    from .checks import check_github_structure, check_ondisk_structure
    from .schema import load_schemas

    project_errors = {}

    for project in sorted(projects):
        schemas = projects[project]
        loaded_schema = load_schemas(*[open(s).read() for s in schemas])

        click.echo(f"Checking {project}…")
        # Surely this assumption will never break...
        if "://" in project:
            repo = urlparse(project).path[1:]
            project_errors[project] = check_github_structure(loaded_schema, repo, access_token)
        else:
            project_errors[project] = check_ondisk_structure(loaded_schema, project)

    click.echo()
    click.echo("Results")
    click.echo("*******")
    any_errors = False
    for project, errors in project_errors.items():
        if errors:
            any_errors = True
            click.echo(f"{project}: Has errors")
            click.echo("\n".join(errors))
        else:
            click.echo(f"{project}: Success!")

        click.echo()

    if any_errors:
        return 1
    else:
        return 0


@dirschema.command()
@click.option("-s", "--schema", multiple=True)
@click.argument("project_dir_or_repo", nargs=-1)
@click.pass_context
def check_projects(ctx, schema, project_dir_or_repo):
    access_token = ctx.obj.get("access_token")
    projects = {p: schema for p in project_dir_or_repo}
    sys.exit(do_check_projects(projects, access_token))


@dirschema.command()
@click.argument("manifest", nargs=1)
@click.pass_context
def check_manifest(ctx, manifest):
    from .schema import load_manifest

    access_token = ctx.obj.get("access_token")
    manifest_dir = Path(manifest).parent
    loaded = load_manifest(open(manifest).read())

    projects = defaultdict(list)
    for grouping in loaded.values():
        for project in grouping["projects"]:
            projects[project].append(str(manifest_dir / Path(grouping["schema"])))

    sys.exit(do_check_projects(projects, access_token))
