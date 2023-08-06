"""Simple calculator.

Implemeted as a Python expression evaluator.
"""

from math import *

import click


@click.command()
@click.argument("expression")
def calc(expression):
    """Compute simple expressions."""

    print(eval(expression))


if __name__ == "__main__":
    calc()
