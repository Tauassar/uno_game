import asyncio
import typing

import backoff
import sqlalchemy

from sqlalchemy.ext import asyncio as sqlalchemy_async
import sqlalchemy.orm

from . import conf


metadata = sqlalchemy.MetaData()

_engine: typing.Optional[sqlalchemy_async.AsyncEngine] = None
_session_factory: typing.Optional[sqlalchemy_async.AsyncEngine] = None
_AsyncScopedSession: typing.Optional[type] = None


class PostgresException(Exception):
    """Raises on internal PostgreSQL related errors."""


@backoff.on_exception(backoff.expo, ConnectionError)
async def connect(
    postgres_uri,
    force_rollback=False,
    min_pool_size: typing.Optional[int] = None,
    max_pool_size: typing.Optional[int] = None,
    connect_timeout: typing.Optional[int] = None,
    command_timeout: typing.Optional[int] = None,
):
    """Connect to the available PostgreSQL cluster and create the session."""
    # TODO: Min pool size, max pool size, connection timeout, command timeout
    global _engine
    global _session_factory
    global _AsyncScopedSession

    if _engine is not None:
        return

    _engine = sqlalchemy_async.create_async_engine(
        postgres_uri,
        pool_pre_ping=True,
        echo=False,
        pool_size=conf.postgres.pool_size,
    )
    _session_factory = sqlalchemy.orm.sessionmaker(
        _engine,
        class_=sqlalchemy_async.AsyncSession,
    )
    _AsyncScopedSession = sqlalchemy_async.async_scoped_session(
        _session_factory,
        scopefunc=asyncio.current_task,
    )

    async with _AsyncScopedSession() as session:
        await session.execute(sqlalchemy.text('select 1;'))


async def disconnect():
    """Disconnect from PostgreSQL cluster and shutdown the session."""
    global _engine

    if _engine is not None:
        _engine = None


def get_session() -> sqlalchemy_async.AsyncSession:
    """Return prepared PostgreSQL session."""
    if _AsyncScopedSession is None:
        raise PostgresException('PostgreSQL session was not initialized properly')

    return _AsyncScopedSession()
