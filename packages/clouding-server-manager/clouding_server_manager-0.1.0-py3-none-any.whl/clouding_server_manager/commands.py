"""Module that contains the CLI commands for the clouding server manager program"""
import json
from typing import List

import click

from .helpers import archive_aux, list_aux, unarchive_aux


@click.command()
@click.option(
    "--api-key",
    "-k",
    type=str,
    required=True,
    help="The API key to use. If not specified directly, the program will try to load the env variable 'CLOUDING_API_KEY'.",  # noqa: E501
    envvar="CLOUDING_API_KEY",
)
@click.option(
    "--targets",
    "-t",
    type=str,
    required=True,
    multiple=True,
    help="The target server or servers to perform the action on. It can either be a single server id, multiple server ids (-t x -t y -t z ...) or all if you want to perform the action on all servers",  # noqa: E501
)
@click.option(
    "--fields",
    "-f",
    type=str,
    required=False,
    default=None,
    multiple=True,
    help="The fields to show. You can either filter by a single field (-f x) or multiple fields (-f x -f y -f z ...). If not specified, all fields will be shown.",  # noqa: E501
)
def list(api_key: str, targets: List[str], fields: List[str]) -> None:
    """
    List all clouding servers or some of them by id

    Args:
        api_key: The API key to use
        targets: The target server or servers to perform the action on

    Raises:
        requests.RequestException: If there was an error with any of the requests
    """
    responses_json = list_aux(api_key, targets, fields)

    # Print the response result for each request (only if there were no errors)
    for r_json in responses_json:  # type: ignore
        click.echo(json.dumps(r_json, indent=4, sort_keys=True))


@click.command()
@click.option(
    "--api-key",
    "-k",
    type=str,
    required=True,
    help="The API key to use. If not specified directly, the program will try to load the env variable 'CLOUDING_API_KEY'.",  # noqa: E501
    envvar="CLOUDING_API_KEY",
)
@click.option(
    "--targets",
    "-t",
    type=str,
    required=True,
    multiple=True,
    help="The target server or servers to perform the action on. It can either be a single server id, multiple server ids (-t x -t y -t z ...) or all if you want to perform the action on all servers",  # noqa: E501
)
def archive(api_key: str, targets: List[str]) -> None:
    """
    Archive all clouding servers or some of them by id

    Args:
        api_key: The API key to use
        targets: The target server or servers to perform the action on

    Raises:
        requests.RequestException: If there was an error with any of the requests
    """
    responses_json = archive_aux(api_key, targets)

    # Print the response result for each request (only if there were no errors)
    for r_json in responses_json:  # type: ignore
        click.echo(json.dumps(r_json, indent=4, sort_keys=True))


@click.command()
@click.option(
    "--api-key",
    "-k",
    type=str,
    required=True,
    help="The API key to use. If not specified directly, the program will try to load the env variable 'CLOUDING_API_KEY'.",  # noqa: E501
    envvar="CLOUDING_API_KEY",
)
@click.option(
    "--targets",
    "-t",
    type=str,
    required=True,
    multiple=True,
    help="The target server or servers to perform the action on. It can either be a single server id, multiple server ids (-t x -t y -t z ...) or all if you want to perform the action on all servers",  # noqa: E501
)
def unarchive(api_key: str, targets: List[str]) -> None:
    """
    Unarchive all clouding servers or some of them by id

    Args:
        api_key: The API key to use
        targets: The target server or servers to perform the action on

    Raises:
        requests.RequestException: If there was an error with any of the requests
    """
    responses_json = unarchive_aux(api_key, targets)

    # Print the response result for each request (only if there were no errors)
    for r_json in responses_json:  # type: ignore
        click.echo(json.dumps(r_json, indent=4, sort_keys=True))
