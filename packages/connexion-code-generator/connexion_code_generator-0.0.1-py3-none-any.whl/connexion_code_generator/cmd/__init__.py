from __future__ import annotations

import click

from connexion_code_generator.__about__ import __version__

from .generate import generate


@click.group(context_settings={"help_option_names": ["-h", "--help"]}, invoke_without_command=True)
@click.version_option(version=__version__, prog_name="connexion protocol generator")
def cli() -> None:
    pass


cli.add_command(generate)
