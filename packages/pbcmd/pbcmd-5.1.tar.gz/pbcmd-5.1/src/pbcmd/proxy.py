"""Start a ssh based socks proxy using autossh."""

import shlex

import click
from subprocess import run, CalledProcessError


@click.command()
@click.option(
    "-p", "--port", default=12001, show_default=True, help="Local port to listen on."
)
@click.option("-v", "--verbose", count=True, help="Verbosity level.")
@click.argument("host", type=str, nargs=1)
def proxy(port, verbose, host):
    """Start a ssh proxy on local port to remove host."""
    click.secho(f"Starting proxy to {host} on port {port}", fg="green")

    options = f"""
        -M 0
        -S none
        -o ServerAliveInterval=10
        -o ServerAliveCountMax=3
        -o ExitOnForwardFailure=yes
        -o BatchMode=yes
        -N
        -D
        127.0.0.1:{port}
        """
    options = shlex.split(options)

    for _ in range(verbose):
        options.append("-v")

    cmd = ["autossh"] + options + [host]
    try:
        run(cmd, check=True)
    except CalledProcessError as e:
        click.secho(f"Proxy command failed\n{e}", fg="red")

if __name__ == "__main__":
    proxy()
