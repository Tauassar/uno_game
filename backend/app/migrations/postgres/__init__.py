import contextlib
import pathlib
import typing

import sqlalchemy.engine
import sqlalchemy.ext.asyncio


ALEMBIC_INI_PATH = str(pathlib.Path(__file__).resolve().parent / 'alembic.ini')


@contextlib.asynccontextmanager
async def connection(url: str, database: typing.Optional[str] = None):
    url = sqlalchemy.engine.make_url(url).set(database=database)
    engine = sqlalchemy.ext.asyncio.create_async_engine(
        url, isolation_level='AUTOCOMMIT', future=True)
    try:
        async with engine.begin() as conn:
            yield conn
    finally:
        await engine.dispose()
