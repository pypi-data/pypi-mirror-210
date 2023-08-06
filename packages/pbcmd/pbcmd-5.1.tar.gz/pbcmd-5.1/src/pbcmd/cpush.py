"""Code push."""

import sys
import shlex
from pathlib import Path
from datetime import datetime
from typing import Union, NewType, cast
from subprocess import run, CalledProcessError

import json5
import click
from pydantic import BaseModel, ValidationError
from pydantic.types import DirectoryPath

LOCAL_CONFIG_FILE = ".cpush.json5"
GLOBAL_CONFIG_FILE = Path("~/.config/cpush/cpush.json").expanduser()
ROOT = Path("/")


RemotePath = NewType("RemotePath", str)
BorgRepo = NewType("BorgRepo", Path)


def ensure_endslash(text: Union[Path, str]) -> str:
    """Ensure path ends with a /."""
    text = str(text)
    if not text.endswith("/"):
        text += "/"
    return text


def run_(cmd: Union[str, list[str]], errormsg: str):
    """Run the command with given error message."""
    if isinstance(cmd, str):
        cmd = shlex.split(cmd)

    try:
        run(cmd, check=True)
    except CalledProcessError as e:
        raise RuntimeError(f"{errormsg}\n{cmd=}") from e


def borg_init(repo: BorgRepo):
    """Initlize a borg repository."""
    click.secho("Initalizing borg repo", fg="yellow")

    cmd = f"borg init --encryption none '{repo}'"
    run_(cmd, errormsg="Failed to initalize borg repo")


def borg_create(archive: str, local_dir: Path, repo: BorgRepo):
    """Create a archive into the borg repo."""
    click.secho(f"Creating archive: {archive}", fg="yellow")

    cmd = f"borg create '{repo}::{archive}' '{local_dir}'"
    run_(cmd, errormsg="Failed to create borg archive")


def borg_prune(repo: BorgRepo):
    """Prune the borg repo."""
    click.secho("Pruning borg repo", fg="yellow")

    cmd = f"""
        borg prune
            --keep-within 2d
            --keep-daily 7
            --keep-weekly 5
            --keep-monthly 6
            '{repo}'
        """
    run_(cmd, errormsg="Failed to prune repository")


def rsync_pull(remote_dir: RemotePath, local_dir: Path):
    """Rsync the contents of the remote directory into local directory."""
    click.secho("Pulling data from remote directory", fg="yellow")

    remote_dir_es = ensure_endslash(remote_dir)
    local_dir_es = ensure_endslash(local_dir)

    cmd = f"""
        rsync
            --archive
            --verbose
            --compress
            --delete
            '{remote_dir_es}'
            '{local_dir_es}'
        """
    run_(cmd, errormsg="Failed to pull from remote directory")


def rsync_push(remote_dir: RemotePath, local_dir: Path):
    """Rsync the contents of the local directory into remote directory."""
    click.secho("Pushing data to remote directory", fg="yellow")

    remote_dir_es = ensure_endslash(remote_dir)
    local_dir_es = ensure_endslash(local_dir)

    cmd = f"""
        rsync
            --archive
            --verbose
            --compress
            --delete
            '{local_dir_es}'
            '{remote_dir_es}'
        """
    run_(cmd, errormsg="Failed to push to remote directory")


def find_config(cwd: Path) -> Path:
    """Find the config file."""
    while cwd != ROOT:
        path = cwd / LOCAL_CONFIG_FILE
        if path.is_file():
            return path

        cwd = cwd.parent

    raise RuntimeError("Local config file not found")


class LocalConfig(BaseModel):
    """Local configuration."""

    project: str
    remotes: dict[str, RemotePath]


class GlobalConfig(BaseModel):
    """Global configuration."""

    backup_dir: DirectoryPath


def do_cpush(
    gconfig: GlobalConfig, lconfig: LocalConfig, remote: str, project_dir: Path
):
    click.secho(f"Using remote: {remote}", fg="yellow")

    remote_dir = lconfig.remotes[remote]
    backup_dir = gconfig.backup_dir / lconfig.project / remote / "remote_backup"
    borg_repo = gconfig.backup_dir / lconfig.project / "borg_repo"

    borg_repo = cast(BorgRepo, borg_repo)

    if not backup_dir.is_dir():
        backup_dir.mkdir(0o700, parents=True, exist_ok=True)
    if not borg_repo.is_dir():
        borg_init(borg_repo)

    now = datetime.now().replace(microsecond=0).isoformat()

    borg_create(f"local-{now}", project_dir, borg_repo)
    rsync_pull(remote_dir, backup_dir)
    borg_create(f"{remote}-{now}", backup_dir, borg_repo)
    borg_prune(borg_repo)
    rsync_push(remote_dir, project_dir)


@click.command()
@click.argument("to", type=str, default="ALL")
def cpush(to: str):
    """Push code to remote directory.

    pb cpush <remote>
    """
    try:
        gconfig = GLOBAL_CONFIG_FILE.read_text()
        gconfig = json5.loads(gconfig)
        gconfig = GlobalConfig.parse_obj(gconfig)

        lconfig = find_config(Path.cwd())
        project_dir = lconfig.parent

        lconfig = lconfig.read_text()
        lconfig = json5.loads(lconfig)
        lconfig = LocalConfig.parse_obj(lconfig)

        if to == "ALL":
            for remote in list(lconfig.remotes.keys()):
                do_cpush(
                    gconfig=gconfig,
                    lconfig=lconfig,
                    remote=remote,
                    project_dir=project_dir,
                )
        else:
            if to in lconfig.remotes:
                remote = to
                do_cpush(
                    gconfig=gconfig,
                    lconfig=lconfig,
                    remote=remote,
                    project_dir=project_dir,
                )
            else:
                raise click.UsageError(f"Remote {to} not defined in local config.")

        click.secho("Code push finished completed successfully", fg="green")
    except (RuntimeError, FileNotFoundError, ValidationError) as e:
        click.secho(e, fg="red")
        sys.exit(1)


if __name__ == "__main__":
    cpush()
