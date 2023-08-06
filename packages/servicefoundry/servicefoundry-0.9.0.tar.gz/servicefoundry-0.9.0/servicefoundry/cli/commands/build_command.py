import json

import rich_click as click

from servicefoundry import builder
from servicefoundry.cli.const import GROUP_CLS
from servicefoundry.cli.util import handle_exception_wrapper


@click.group(
    name="build",
    cls=GROUP_CLS,
    invoke_without_command=True,
    help="Build docker image locally from Truefoundry spec",
)
@click.option(
    "--name",
    type=click.STRING,
    required=True,
    help="Name for the image being build - used as docker tag",
)
@click.option(
    "--build-config",
    "--build_config",
    type=click.STRING,
    required=True,
    help="Build part of the spec as a json spec",
)
@click.option(
    "--cache",
    type=click.STRING,
    default=None,
    help="Docker repository to use as a cache to pull layers from",
)
@handle_exception_wrapper
def build_command(name, cache, build_config):
    if build_config:
        builder.build(
            build_configuration=json.loads(build_config), tag=name, cache_from=cache
        )
        return


def get_build_command():
    return build_command
