import click

from swh.core.cli import CONTEXT_SETTINGS
from swh.core.cli import swh as swh_cli_group


@swh_cli_group.group(name="spdx", context_settings=CONTEXT_SETTINGS)
@click.pass_context
def spdx_cli_group(ctx):
    """spdx main command."""


@spdx_cli_group.command()
@click.option("--bar", help="Something")
@click.pass_context
def bar(ctx, bar):
    """Do something."""
    click.echo("bar")
