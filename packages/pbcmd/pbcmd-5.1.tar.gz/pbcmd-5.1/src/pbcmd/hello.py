"""Hello world command."""

import click
from click import secho

@click.command()
def hello():
    """Print "Hello, world!"."""
    secho("Hello, world!", fg="green")

if __name__ == "__main__":
    hello()
