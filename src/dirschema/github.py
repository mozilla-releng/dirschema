import logging
import time
from base64 import b64decode
from collections import defaultdict

import jwt
import requests
from flask import Blueprint, Flask, current_app, request
from github import Github
from github.Consts import mediaTypeIntegrationPreview
from github.MainClass import DEFAULT_BASE_URL

from .checks import check_github_structure, error_report
from .schema import load_manifest, load_schemas

logger = logging.getLogger("dirschema")


def get_installation_token(installation_id):
    private_key = current_app.config["GITHUB_PRIVATE_KEY"]
    app_id = current_app.config["GITHUB_APP_ID"]
    now = int(time.time())
    payload = {"iat": now, "exp": now + 600, "iss": app_id}
    access_token = jwt.encode(payload, private_key, algorithm="RS256").decode("utf-8")
    ret = requests.post(
        f"{DEFAULT_BASE_URL}/app/installations/{installation_id}/access_tokens",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Accept": mediaTypeIntegrationPreview,
            "User-Agent": "dirschema",
        },
    )
    ret.raise_for_status()
    return ret.json()["token"]


def check_repo(repo, ref, full_name, token):
    manifest = b64decode(repo.get_contents(".dirschema.yml", ref=ref).content).decode("utf-8")
    loaded = load_manifest(manifest)

    projects = defaultdict(list)
    for grouping in loaded.values():
        for project in grouping["projects"]:
            projects[project].append(grouping["schema"])

    project_errors = {}

    for project in sorted(projects):
        schemas = projects[project]
        loaded_schema = load_schemas(*[requests.get(s).text for s in schemas])

        logging.debug(f"Checking {project}…")
        # TODO: update this function to take a repo instead of a name/token
        results = check_github_structure(loaded_schema, full_name, token, project.lstrip("/"), ref)
        if len(results) > 0:
            project_errors[project] = results

    return project_errors


def handle_push(payload):
    # TODO: figure how to avoid handling push event if it's part of a PR
    token = get_installation_token(payload["installation"]["id"])
    g = Github(token)
    full_name = payload["repository"]["full_name"]
    ref = payload["after"]
    repo = g.get_repo(full_name)
    commit = repo.get_commit(ref)
    commit.create_status("pending", context="dirschema")
    try:
        project_errors = check_repo(repo, ref, full_name, token)

        if project_errors:
            logger.debug("Found errors")
            commit.create_status("failure", context="dirschema")
            commit.create_comment(error_report(project_errors))
        else:
            logger.debug("Success!")
            commit.create_status("success", context="dirschema")
    except Exception as e:
        commit.create_status("error", context="dirschema")
        raise e


def handle_pull_request(payload):
    if payload["action"] not in ("opened", "reopened", "synchronize"):
        logger.debug("Skipping pull request event that is not opened, reopened, or synchronize")
        return "OK"

    token = get_installation_token(payload["installation"]["id"])
    g = Github(token)
    full_name = payload["repository"]["full_name"]
    ref = payload["pull_request"]["head"]["sha"]
    pull_number = payload["number"]
    repo = g.get_repo(full_name)
    root_files = [i.name for i in repo.get_contents(".", ref=ref)]
    if ".dirschema.yml" not in root_files:
        # Nothing to do!
        return

    commit = repo.get_commit(ref)
    commit.create_status("pending", context="dirschema")
    pull_request = repo.get_pull(pull_number)
    try:
        project_errors = check_repo(repo, ref, full_name, token)

        if project_errors:
            logger.debug("Found errors")
            commit.create_status("failure", context="dirschema")
            pull_request.create_issue_comment(error_report(project_errors))
        else:
            logger.debug("Success!")
            commit.create_status("success", context="dirschema")
    except Exception as e:
        commit.create_status("error", context="dirschema")
        raise e


# TODO: re-enable push handler when we figure out how to avoid double commenting
# on pull requests
# event_handlers = {"push": handle_push, "pull_request": handle_pull_request}
event_handlers = {"pull_request": handle_pull_request}

github_app = Blueprint("github_app", __name__)


@github_app.route("/github_event", methods=("POST",))
def handle_event():
    event_type = request.headers["X-Github-Event"]
    if event_type in event_handlers:
        logger.debug(f"Handling {event_type} event")
        event_handlers[event_type](request.json)
    else:
        logger.debug(f"Ignoring event type: {event_type}")

    return "OK"


def create_app(private_key, app_id):
    app = Flask("dirschema")
    app.config["GITHUB_PRIVATE_KEY"] = private_key
    app.config["GITHUB_APP_ID"] = app_id
    app.register_blueprint(github_app)
    return app
