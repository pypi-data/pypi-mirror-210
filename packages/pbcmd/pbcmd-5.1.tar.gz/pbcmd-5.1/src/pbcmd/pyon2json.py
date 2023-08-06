"""Python object notation to JSON."""

import json
from pathlib import Path

import click


def do_pyon2json(ifname, ofname, pretty=True):
    """Convert the python object notation file to json object notation file."""
    with open(ifname, "r") as fin:
        x = fin.read()

    x = eval(x)

    if pretty:
        x = json.dumps(x, indent=2, sort_keys=True)
    else:
        x = json.dumps(x)

    with open(ofname, "w") as fout:
        fout.write(x)


@click.command()
@click.option("-i", "--input", "ifname", type=str, default=None, help="Input file name")
@click.option(
    "-o", "--output", "ofname", type=str, default=None, help="Output file name"
)
@click.option("-s", "--suffix", default=".json", help="Output file suffix")
@click.option("--pretty/--no-pretty", help="Output pretty json")
@click.argument("files", type=str, nargs=-1)
def pyon2json(ifname, ofname, suffix, pretty, files):
    """Convert the files from PYON to JSON."""
    if not ifname and not files:
        raise click.UsageError("No input files provided")

    if ifname and files:
        raise click.UsageError("Both --input and files can't be specified")

    if ifname:
        ifnames = [Path(ifname)]
    else:
        ifnames = [Path(f) for f in files]

    if len(ifnames) > 1 and ofname:
        raise click.UsageError("--output specified with multiple input files")

    if ofname:
        ofnames = [ofname]
    else:
        ofnames = []
        for ifname in ifnames:
            ofname = ifname.with_suffix(suffix)
            ofnames.append(ofname)

    for ifname, ofname in zip(ifnames, ofnames):
        do_pyon2json(ifname, ofname, pretty)


if __name__ == "__main__":
    pyon2json()
