"""Manage timestamped files."""

from pathlib import Path

import click


@click.command()
@click.option(
    "-d",
    "--directory",
    type=click.Path(file_okay=False, dir_okay=True, exists=True),
    required=True,
    help="The directory to remove files from.",
)
@click.option(
    "-p", "--prefix", type=str, required=True, help="Prefix of the files to be removed."
)
@click.option(
    "-s", "--suffix", type=str, required=True, help="Suffix of the files to be removed."
)
@click.option(
    "-da",
    "--delete-after",
    type=int,
    required=True,
    help="Only delete files with timestamp after this time (inclusive).",
)
@click.option(
    "-db",
    "--delete-before",
    type=int,
    required=True,
    help="Only delete files with timestamp before this time (exclusive). ",
)
@click.option(
    "-dr",
    "--dry-run",
    is_flag=True,
    help="If specified don't do the actual file deletion.",
)
def rm_timestamped(directory, prefix, suffix, delete_after, delete_before, dry_run):
    """Remove timestamped files from the given directory.

    Files should have names of the form <prefix><unix-timestamp><suffix>.
    """
    directory = Path(directory)

    n_files = 0
    n_deleted = 0
    for fname in directory.iterdir():
        n_files += 1
        x = str(fname)
        if x.startswith(prefix) and x.endswith(suffix):
            x = x[len(prefix) :]
            x = x[: -len(suffix)]
            try:
                x = int(x)
            except ValueError:
                continue

            if delete_after <= x < delete_before:
                n_deleted += 1
                print("Deleting: '%s'" % fname)

                if not dry_run:
                    fname.unlink()

    click.secho("Found %d files" % n_files, color="green")
    click.secho("Deleted %d files" % n_deleted, color="green")


if __name__ == "__main__":
    rm_timestamped()
