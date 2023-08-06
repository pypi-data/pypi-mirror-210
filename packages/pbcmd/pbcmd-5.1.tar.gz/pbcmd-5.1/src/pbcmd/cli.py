"""CLI interface."""

import click

from .hello import hello
from .calc import calc
from .proxy import proxy
from .timefmt import timefmt
from .git import git
from .pyon2json import pyon2json
from .csplit import csplit
from .cpush import cpush

# from .rm_timestamped import rm_timestamped
from .obscure import obscure, unobscure
from .mail import mail


@click.group()
def cli():
    """PB's command line tools."""


cli.add_command(hello)
cli.add_command(calc)
cli.add_command(proxy)
cli.add_command(timefmt)
cli.add_command(git)
cli.add_command(pyon2json)
cli.add_command(csplit)
cli.add_command(cpush)
# cli.add_command(rm_timestamped)
cli.add_command(obscure)
cli.add_command(unobscure)
cli.add_command(mail)

if __name__ == "__main__":
    cli(prog_name="pb")
