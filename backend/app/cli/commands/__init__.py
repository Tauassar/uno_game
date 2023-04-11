import click

from . import alembic


cli = click.Group(
    context_settings={
        'max_content_width': 95,
    },
)
cli.add_command(alembic.execute_alembic)