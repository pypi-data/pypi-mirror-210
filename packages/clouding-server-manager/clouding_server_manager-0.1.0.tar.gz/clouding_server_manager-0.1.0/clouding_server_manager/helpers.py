"""Module with helper functions for the clouding server manager CLI"""
import datetime
import time
from typing import Any, Dict, List

import click
import requests

from .constants import (
    API_ALREADY_ARCHIVED_ERROR_MESSAGE,
    API_ALREADY_UNARCHIVED_ERROR_MESSAGE,
    BASE_URL,
    MAX_TOTAL_WAIT_TIME,
    WAIT_TIME,
)


def list_aux(api_key: str, targets: List[str], fields: List[str] = []) -> List[Dict[str, Any]]:
    """
    List all clouding servers or some of them by id (business logic)

    Args:
        api_key: The API key to use
        targets: The target server or servers to perform the action on
        fields: The fields to show in the responses

    Raises:
        requests.RequestException: If there was an error with any of the requests

    Returns:
        A list with all the responses to the listing requests
    """
    click.secho("[LIST] Listing servers...", fg="blue")

    HEADERS = {"Content-Type": "application/json", "X-API-KEY": api_key}
    REQUEST_URL = f"{BASE_URL}/servers"

    responses_json: List[Dict[str, Any]] = []
    # Check if the user wants to list all servers or just some of them by id
    if "all" in targets:
        response = requests.get(REQUEST_URL, headers=HEADERS)
        if response.status_code == 200:
            for server in response.json()["servers"]:
                responses_json.append(server)
        else:
            raise requests.RequestException(f"Error: {response.status_code} {response.reason}")
    else:
        for target in targets:
            response = requests.get(f"{REQUEST_URL}/{target}", headers=HEADERS)
            if response.ok:
                responses_json.append(response.json())
            else:
                raise requests.RequestException(f"Error: {response.status_code} {response.reason}")

    # Filter the fields if the user specified any
    if fields:
        click.secho("[LIST SEVERS] Filtering fields...", fg="blue")
        responses_json = [{field: server.get(field, "Invalid field") for field in fields} for server in responses_json]

    return responses_json


def get_all_server_ids(api_key: str) -> List[str]:
    """
    Get all the server ids

    Args:
        api_key: The API key to use

    Raises:
        requests.RequestException: If there was an error with any of the requests

    Returns:
        A list with all server ids
    """
    return [server["id"] for server in list_aux(api_key, ["all"])]


def archive_aux(api_key: str, targets: List[str]) -> List[Dict[str, Any]]:
    """
    Archive all clouding servers or some of them by id (business logic)

    Args:
        api_key: The API key to use
        targets: The target server or servers to perform the action on

    Raises:
        requests.RequestException: If there was an error with any of the requests

    Returns:
        A list with all the responses to the archiving requests
    """
    click.secho("[ARCHIVE] Archiving servers...", fg="blue")

    HEADERS = {"Content-Type": "application/json", "X-API-KEY": api_key}

    responses_json: List[Dict[str, Any]] = []
    if "all" in targets:
        # Get all server ids if the user wants to archive all servers
        targets = get_all_server_ids(api_key)

    # Make unarchive requests until all servers have been archived or total wait time is exceeded
    waited_time = 0
    while targets and waited_time < MAX_TOTAL_WAIT_TIME:
        for target in targets:
            response = requests.post(f"{BASE_URL}/servers/{target}/archive", headers=HEADERS)

            if response.ok:
                responses_json.append(response.json())
            # If there is an error, we check if it is because the server is already archived
            elif (
                response.status_code == 400
                and response.json()["errors"]["server-state"][0] == API_ALREADY_ARCHIVED_ERROR_MESSAGE
            ):
                # If the server is already archived or has been archived, we remove it from the targets list
                targets.remove(target)
            elif not response.ok:
                raise requests.RequestException(f"Error: {response.status_code} {response.reason}")

        # Wait some time before making the next batch of requests if there are still servers to archive
        if targets:
            click.secho("[ARCHIVE] Some servers are still being archived...", fg="blue")
            click.secho(f"[ARCHIVE] Waiting {WAIT_TIME} seconds before checking again...", fg="blue")
            time.sleep(WAIT_TIME)
            waited_time += WAIT_TIME

    click.secho("[ARCHIVE] All servers have been archived!", fg="blue")

    # Change server status to completed in the responses and add completed at date
    completed_at_date = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    responses_json = [
        {**response, "status": "completed", "completedAt": completed_at_date} for response in responses_json
    ]

    return responses_json


def unarchive_aux(api_key: str, targets: List[str]) -> List[Dict[str, Any]]:
    """
    Unarchive all clouding servers or some of them by id (business logic)

    Args:
        api_key: The API key to use
        targets: The target server or servers to perform the action on

    Raises:
        requests.RequestException: If there was an error with any of the requests
    """
    click.secho("[UNARCHIVE] Unarchiving servers...", fg="blue")

    HEADERS = {"Content-Type": "application/json", "X-API-KEY": api_key}

    responses_json: List[Dict[str, Any]] = []
    if "all" in targets:
        # Get all server ids if the user wants to unarchive all servers
        targets = get_all_server_ids(api_key)

    # Make unarchive requests until all servers have been unarchived or total wait time is exceeded
    waited_time = 0
    while targets and waited_time < MAX_TOTAL_WAIT_TIME:
        for target in targets:
            response = requests.post(f"{BASE_URL}/servers/{target}/unarchive", headers=HEADERS)

            if response.ok:
                responses_json.append(response.json())
            # If there is an error, we check if it is because the server is already unarchived
            elif (
                response.status_code == 400
                and response.json()["errors"]["server-state"][0] == API_ALREADY_UNARCHIVED_ERROR_MESSAGE
            ):
                # If the server is already unarchived or has been unarchived, we remove it from the targets list
                targets.remove(target)
            elif not response.ok:
                raise requests.RequestException(f"Error: {response.status_code} {response.reason}")

        # Wait some time before making the next batch of requests if there are still servers to unarchive
        if targets:
            click.secho("[UNARCHIVE] Some servers are still being unarchived...", fg="blue")
            click.secho(f"[UNARCHIVE] Waiting {WAIT_TIME} seconds before checking again...", fg="blue")
            time.sleep(WAIT_TIME)
            waited_time += WAIT_TIME

    click.secho("[UNARCHIVE] All servers have been unarchived!", fg="blue")

    # Change server status to completed in the responses and add completed at date
    completed_at_date = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    responses_json = [
        {**response, "status": "completed", "completedAt": completed_at_date} for response in responses_json
    ]

    return responses_json
