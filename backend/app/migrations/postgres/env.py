import asyncio
import logging.config

import alembic.context
import sqlalchemy.ext.asyncio

import app.api.models  # noqa: F401
import app.core.conf
import app.core.postgres


config = alembic.context.config


logging.config.fileConfig(config.config_file_name)


def apply_migrations(connection):
    alembic.context.configure(
        connection=connection,
        target_metadata=app.core.postgres.metadata,
    )
    with alembic.context.begin_transaction():
        alembic.context.run_migrations()


async def run_migrations():
    engine = sqlalchemy.ext.asyncio.create_async_engine(
        url=app.core.conf.postgres.uri,
    )

    async with engine.begin() as connection:
        await connection.run_sync(apply_migrations)


asyncio.run(run_migrations())
