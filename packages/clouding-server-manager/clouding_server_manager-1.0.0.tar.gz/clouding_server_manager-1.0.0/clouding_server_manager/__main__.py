"""Main entry point for the CLI"""
import click
import requests
from dotenv import load_dotenv

from .commands import archive, list, unarchive


@click.group()
def commands():
    pass


# Add the commands to the group
commands.add_command(archive)
commands.add_command(list)
commands.add_command(unarchive)


def main():
    """Entry point for the CLI"""
    # Load API key from env variable
    load_dotenv()

    # Run the CLI
    try:
        commands()
    except requests.RequestException as e:
        click.secho(e, fg="red")
        exit(1)


if __name__ == "__main__":
    main()
