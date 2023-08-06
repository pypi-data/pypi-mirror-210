import collections
import os
from typing import Any, Dict, Iterator, List

import docker
from docker.errors import APIError, BuildError
from pydantic import BaseModel
from rich.console import Console

from servicefoundry.lib.clients.shell_client import Shell
from servicefoundry.logger import logger

__all__ = [
    "build_docker_image",
    "push_docker_image",
    "pull_docker_image",
    "push_docker_image_with_latest_tag",
    "env_has_docker",
]

PROGRESS_PERCENTAGE_DELTA = 20


class LastShownProgress(BaseModel):
    class Config:
        allow_mutation = True

    status: str = "Unknown"
    percentage: float = -1000.0


def _handle_layer_pull_progress_log(
    log_dict: Dict[str, Any], layer_last_shown_progress
):
    should_log = False
    id_, progress_detail, status = (
        log_dict["id"],
        log_dict.get("progressDetail", {}),
        log_dict["status"],
    )
    line_parts = [f"{id_}:", f"{status}"]
    if status != layer_last_shown_progress[id_].status:
        # Print if status of the layer has changed e.g. Downloading -> Extracting
        should_log = True
        layer_last_shown_progress[id_].status = status
    if not progress_detail:
        # If there is no progress information, reset last shown percentage
        layer_last_shown_progress[id_].percentage = -1000.0
    else:
        completed = progress_detail.get("current")
        total = progress_detail.get("total")
        if completed is not None and total is not None:
            last = layer_last_shown_progress[id_].percentage
            current = float(completed) / float(total) * 100.0
            # Print if the stage is 100% complete or progress of >= PROGRESS_PERCENTAGE_DELTA% was made over last time
            if (
                current >= 100.0
                or current // PROGRESS_PERCENTAGE_DELTA
                > last // PROGRESS_PERCENTAGE_DELTA
            ):
                should_log = True
                line_parts.append(
                    f"{float(completed) / 1e6:.3f}MB/{float(total) / 1e6:.3f}MB ({current:.2f}%)"
                )
                layer_last_shown_progress[id_].percentage = current
    return line_parts if should_log else []


def _stream_docker_build_logs(logs: Iterator[Dict[str, Any]]):
    console = Console(color_system=None, markup=False, soft_wrap=True)
    layer_last_shown_progress = collections.defaultdict(LastShownProgress)
    for log_dict in logs:
        parts = []
        if "id" in log_dict and "status" in log_dict:
            # If this line is a potential progress bar line
            parts = _handle_layer_pull_progress_log(log_dict, layer_last_shown_progress)
        else:
            for value in log_dict.values():
                line = str(value)
                if line.strip():
                    parts.append(line.rstrip())
        if parts:
            console.print(" ".join(parts))


def _get_docker_client():
    try:
        return docker.from_env()
    except Exception as ex:
        raise Exception("Could not connect to Docker") from ex


def env_has_docker():
    try:
        _get_docker_client()
        return True
    except Exception as ex:
        return False


# this is required since push does throw an error if it
# fails - so we have to parse the response logs to catch the error
# the other option is to run `docker login` as a subprocess, but it's
# not recommended to provide password to subprocess
def catch_error_in_push(response: List[dict]):
    for line in response:
        if line.get("error") is not None:
            raise Exception(
                f'Failed to push to registry with message \'{line.get("error")}\''
            )


def build_docker_image(
    path: str, tag: str, platform: str, dockerfile: str, cache_from: List[str]
):
    use_depot = bool(os.environ.get("USE_DEPOT"))
    depot_project_id = os.environ.get("DEPOT_PROJECT_KEY")
    logger.info("Starting docker build...")
    if use_depot and depot_project_id:
        try:
            Shell().execute_shell_command(
                [
                    "depot",
                    "build",
                    "--project",
                    depot_project_id,
                    "-f",
                    dockerfile,
                    "-t",
                    tag,
                    path,
                    "--push",
                ]
            )
        except Exception as e:
            raise Exception("Error while building Docker image using Depot") from e
    else:
        try:
            # TODO (chiragjn): Maybe consider using client.images.build
            build_logs = _get_docker_client().api.build(
                decode=True,
                path=path,
                tag=tag,
                platform=platform,
                dockerfile=dockerfile,
                cache_from=cache_from,
            )
            _stream_docker_build_logs(build_logs)
        except (BuildError, APIError) as e:
            raise Exception("Error while building Docker image") from e


def push_docker_image(
    image_uri: str,
    docker_login_username: str,
    docker_login_password: str,
):
    client = _get_docker_client()
    auth_config = {"username": docker_login_username, "password": docker_login_password}

    logger.info(f"Pushing {image_uri}")
    response = client.images.push(
        repository=image_uri, auth_config=auth_config, decode=True, stream=True
    )
    catch_error_in_push(response=response)


def push_docker_image_with_latest_tag(
    image_uri: str,
    docker_login_username: str,
    docker_login_password: str,
):
    client = _get_docker_client()
    auth_config = {"username": docker_login_username, "password": docker_login_password}

    repository_without_tag, _ = image_uri.rsplit(":", 1)
    image = client.images.get(image_uri)
    image.tag(repository=repository_without_tag, tag="latest")

    logger.info(f"Pushing {repository_without_tag}:latest")
    response = client.images.push(
        repository=repository_without_tag,
        tag="latest",
        auth_config=auth_config,
        decode=True,
        stream=True,
    )
    catch_error_in_push(response=response)


def pull_docker_image(
    image_uri: str,
    docker_login_username: str,
    docker_login_password: str,
):
    auth_config = {"username": docker_login_username, "password": docker_login_password}
    logger.info(f"Pulling cache image {image_uri}")
    _get_docker_client().images.pull(repository=image_uri, auth_config=auth_config)
