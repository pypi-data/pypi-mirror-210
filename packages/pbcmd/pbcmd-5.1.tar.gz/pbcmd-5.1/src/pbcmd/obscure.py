"""Create obscure/unobscure a text file."""

import zlib
from base64 import urlsafe_b64encode, urlsafe_b64decode

import click


def text_obscure(data):
    """Return the obscured version of the text."""
    data = data.encode("utf-8")
    data = zlib.compress(data, 9)
    data = urlsafe_b64encode(data)
    data = data.decode("ascii")
    return data


def text_unobscure(data):
    """Return the unobscured version of the text."""
    data = data.encode("ascii")
    data = urlsafe_b64decode(data)
    data = zlib.decompress(data)
    data = data.decode("utf-8")
    return data


@click.command()
@click.option(
    "-i",
    "--inplace",
    is_flag=True,
    help="If set the input file will be overwritten inplace",
)
@click.option(
    "-o", "--output", default=None, type=click.Path(), help="Output file name"
)
@click.argument("input")
def obscure(inplace, output, input):
    """Obscure a text file."""
    if inplace:
        output = input
    elif output is None:
        output = f"{input}.obscured"

    with open(input, "rt") as fobj:
        data = fobj.read()

    data = text_obscure(data)

    with open(output, "wt") as fobj:
        fobj.write(data)


@click.command()
@click.option(
    "-i",
    "--inplace",
    is_flag=True,
    help="If set the input file will be overwritten inplace.",
)
@click.option(
    "-o", "--output", default=None, type=click.Path(), help="Output file name"
)
@click.argument("input")
def unobscure(inplace, output, input):
    """Unobscure a text file."""
    if inplace:
        output = input
    elif output is None:
        output = f"{input}.unobscured"

    with open(input, "rt") as fobj:
        data = fobj.read()

    data = text_unobscure(data)

    with open(output, "wt") as fobj:
        fobj.write(data)
