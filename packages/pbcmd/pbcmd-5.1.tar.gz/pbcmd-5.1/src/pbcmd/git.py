"""Git helper commands."""

import socket
import getpass
from datetime import datetime
from subprocess import run, PIPE, DEVNULL

import click
from click import secho


def commit_uncommited():
    """Commit any uncommited changes to current branch."""
    secho("Adding uncommitted changes to git")
    cmd = ["git", "add", "--all", "."]
    cp = run(cmd, check=False)
    if cp.returncode != 0:
        raise RuntimeError("Failed to add changes")

    secho("Committing changes")
    cmd = ["git", "diff", "--cached", "--no-ext-diff", "--quiet", "--exit-code"]
    cp = run(cmd, check=False)
    if cp.returncode == 0:
        secho("Nothing to commit")
        return

    username = getpass.getuser()
    hostname = socket.gethostname()
    now = datetime.now().isoformat()
    commit_message = "Commit by %s@%s at %s" % (username, hostname, now)
    cmd = ["git", "commit", "--message", commit_message]
    cp = run(cmd, check=False)
    if cp.returncode != 0:
        raise RuntimeError("Failed to commit changes")


def rsync_pull(remote_dir):
    """Rsync the contents of the remote directory into current git repo."""
    secho("Pulling from remote directory")
    cmd = [
        "rsync",
        "--archive",
        "--verbose",
        "--compress",
        "--delete",
        "--exclude",
        ".git/",
        remote_dir,
        "./",
    ]
    cp = run(cmd, check=False)
    if cp.returncode != 0:
        raise RuntimeError("Failed to pull from remote directory")


def rsync_push(remote_dir):
    """Rsync the contents of the current git repo into remote directory."""
    secho("Pushing to remote directory")
    cmd = [
        "rsync",
        "--archive",
        "--verbose",
        "--compress",
        "--delete",
        "--exclude",
        ".git/",
        "./",
        remote_dir,
    ]
    cp = run(cmd, check=False)
    if cp.returncode != 0:
        raise RuntimeError("Failed to push to remote directory")


def fetch_all():
    """Execute git fetch --all."""
    secho("Fetching remote updates")
    cmd = ["git", "fetch", "--all"]
    cp = run(cmd, check=False)
    if cp.returncode != 0:
        raise RuntimeError("Failed to pull from remote repos")


def push():
    """Execute a git push."""
    secho("Pushing updates to upstream repo")
    cmd = ["git", "push"]
    cp = run(cmd, check=False)
    if cp.returncode != 0:
        raise RuntimeError("Failed to push updates")


def merge_ff_only(merge_from):
    """Merge updates."""
    secho("Merging updates")
    cmd = ["git", "merge", "--ff-only", merge_from]
    cp = run(cmd, check=False)
    if cp.returncode != 0:
        raise RuntimeError("Failed to merge")


def checkout_branch(branch):
    """Checkout the given branch."""
    secho(f"Checking out branch {branch}")
    if does_branch_exist(branch):
        cmd = ["git", "checkout", branch]
    else:
        cmd = ["git", "checkout", "-b", branch]
    cp = run(cmd, check=False)
    if cp.returncode != 0:
        raise RuntimeError("Failed to checkout branch %s" % branch)


def check_git_repo_top_dir():
    """Check we are at the top directory of a git repo."""
    cmd = ["git", "rev-parse", "--git-dir"]
    cp = run(cmd, stdout=PIPE, stderr=DEVNULL, encoding="utf-8", check=False)
    if cp.returncode != 0:
        raise RuntimeError("Current directory is not inside a git repository")
    if cp.stdout.strip() != ".git":
        raise RuntimeError(
            "Current directory is not the toplevel directory of a git repository"
        )


def get_current_branch():
    """Get the current git branch."""
    cmd = ["git", "rev-parse", "--abbrev-ref", "HEAD"]
    cp = run(cmd, stdout=PIPE, stderr=DEVNULL, encoding="utf-8", check=False)
    branch = cp.stdout.strip()
    if cp.returncode != 0 or not branch:
        raise RuntimeError("Failed to get current branch")
    return branch


def does_branch_exist(branch):
    """Return if a given branch exists."""
    cmd = ["git", "show-ref", "refs/heads/%s" % branch]
    cp = run(cmd, stdout=DEVNULL, stderr=DEVNULL, check=False)
    if cp.returncode == 0:
        return True
    return False


def get_current_upstream():
    """Get the upstream of the current branch."""
    cmd = ["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}"]
    cp = run(cmd, stdout=PIPE, stderr=DEVNULL, encoding="utf-8", check=False)
    if cp.returncode == 0:
        return cp.stdout.strip()
    return None


def is_ahead(a, b):
    """Check if a is ahead of branch b."""
    cmd = ["git", "rev-list", "--count", a, b]
    cp = run(cmd, stdout=PIPE, stderr=DEVNULL, encoding="utf-8", check=False)
    if cp.returncode == 0:
        if cp.stdout.strip() != "0":
            return True
    return False


@click.group()
def git():
    """Git helper commands."""


@git.command()
def sync():
    """Sync local and upstream repository."""
    try:
        check_git_repo_top_dir()
        branch = get_current_branch()
        upstream = get_current_upstream()
        if upstream is None:
            secho("No upstream defined", fg="yellow")
            return

        commit_uncommited()
        fetch_all()
        merge_ff_only(upstream)
        if is_ahead(branch, upstream):
            secho("Local repo is ahead of upstream")
            push()
            secho("Sync completed successfully", fg="green")
        else:
            secho("Nothing to push", fg="yellow")
    except RuntimeError as e:
        secho(str(e), fg="red")


@git.command()
@click.option(
    "-r",
    "--remote-branch",
    type=str,
    default="",
    help="Branch to use to commit remote repository",
)
@click.argument("remote_dir")
def rsync(remote_branch, remote_dir):
    """Sync local repository with a remote directory."""
    if not remote_dir.endswith("/"):
        remote_dir += "/"

    if not remote_branch:
        remote_branch = remote_dir
        remote_branch = [c if c.isalnum() else "_" for c in remote_branch]
        remote_branch = "".join(remote_branch)
        remote_branch = remote_branch.strip("_")
        secho("Using remote branch %s" % remote_branch, fg="green")

    try:
        check_git_repo_top_dir()
        branch = get_current_branch()

        commit_uncommited()

        checkout_branch(remote_branch)
        try:
            rsync_pull(remote_dir)
            commit_uncommited()
        finally:
            checkout_branch(branch)

        rsync_push(remote_dir)

        secho("Rsync completed successfully", fg="green")
    except RuntimeError as e:
        secho(str(e), fg="red")


if __name__ == "__main__":
    git()
