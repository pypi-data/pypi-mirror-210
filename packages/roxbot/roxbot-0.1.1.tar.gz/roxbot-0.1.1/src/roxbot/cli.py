#!/usr/bin/env python3
"""
roxbot CLI
"""

import click

import roxbot as pkg


@click.group()
def cli():
    pass  # pragma: no cover


@cli.command()
def info():
    """Print package info"""
    print(pkg.__version__)


cli.add_command(info)

if __name__ == "__main__":
    cli()  # pragma: no cover
