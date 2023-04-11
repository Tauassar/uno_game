import alembic.config
import click

from ...migrations import postgres as postgres_migrations


@click.command(
    name='alembic',
    help='Execute alembic migration tool with provided arguments',
    context_settings={
        'ignore_unknown_options': True,
        'allow_extra_args': True,
    },
)
@click.argument('alembic_args', nargs=-1, type=click.UNPROCESSED)
def execute_alembic(alembic_args):
    default_alembic_args = ['-c', postgres_migrations.ALEMBIC_INI_PATH]

    alembic.config.main(argv=[*default_alembic_args, *alembic_args])
