import sqlalchemy
import sqlalchemy.dialects
import sqlalchemy.orm

from ...core import postgres
from ...core import times
from .. import schemas
from . import Base


class AccessToken(Base):
    __tablename__ = 'accesstokens'

    user_id = sqlalchemy.Column(
        sqlalchemy.Integer(),
        sqlalchemy.ForeignKey('users.id'),
        nullable=False,
    )
    token = sqlalchemy.Column(
        sqlalchemy.Text(),
        nullable=False,
        unique=True,
        primary_key=True,
    )
    token_type = sqlalchemy.Column(
        sqlalchemy.Text(),
        nullable=False,
        server_default='bearer',
    )
    is_revoked = sqlalchemy.Column(
        sqlalchemy.Boolean(),
        nullable=False,
        server_default='false',
    )
    issued_at = sqlalchemy.Column(
        sqlalchemy.DateTime(timezone=True),
        nullable=False,
        server_default=sqlalchemy.text('now()'),
    )
    expires_in = sqlalchemy.Column(
        sqlalchemy.Integer(),
        nullable=False,
    )
    revoked_at = sqlalchemy.Column(
        sqlalchemy.DateTime(timezone=True),
        nullable=True,
    )

    user = sqlalchemy.orm.relationship(
        'User', backref=sqlalchemy.orm.backref('accesstokens', order_by=issued_at),
    )


class RefreshToken(Base):
    __tablename__ = 'refreshtokens'

    user_id = sqlalchemy.Column(
        sqlalchemy.Integer(),
        sqlalchemy.ForeignKey('users.id'),
        index=True,
        nullable=False,
    )
    token = sqlalchemy.Column(
        sqlalchemy.Text(),
        nullable=False,
        unique=True,
        primary_key=True,
    )
    token_type = sqlalchemy.Column(
        sqlalchemy.Text(),
        nullable=False,
        server_default='bearer',
    )
    is_revoked = sqlalchemy.Column(
        sqlalchemy.Boolean(),
        nullable=False,
        server_default='false',
    )
    issued_at = sqlalchemy.Column(
        sqlalchemy.DateTime(timezone=True),
        nullable=False,
        server_default=sqlalchemy.text('now()'),
    )
    revoked_at = sqlalchemy.Column(
        sqlalchemy.DateTime(timezone=True),
        nullable=True,
    )

    user = sqlalchemy.orm.relationship(
        'User', backref=sqlalchemy.orm.backref('refreshtokens', order_by=issued_at),
    )


def token_access_query():
    return sqlalchemy.select(AccessToken)


def token_refresh_query():
    return sqlalchemy.select(RefreshToken)


async def token_get_access(access_token: str) -> AccessToken:
    query = token_access_query().filter(
        AccessToken.token == access_token,
        AccessToken.is_revoked is False,
    )

    session = postgres.get_session()

    return (await session.execute(query)).scalar_one_or_none()


async def token_get_refresh(refresh_token: str) -> RefreshToken:
    query = token_access_query().filter(
        RefreshToken.token == refresh_token,
        RefreshToken.is_revoked is False,
    )

    session = postgres.get_session()

    return (await session.execute(query)).scalar_one_or_none()


async def token_get_refresh_by_client_id(user_id: int) -> RefreshToken:
    query = token_access_query().filter(
        RefreshToken.user_id == user_id,
        RefreshToken.is_revoked is False,
    )

    session = postgres.get_session()

    return (await session.execute(query)).scalar_one_or_none()


async def token_store_access(access_token: schemas.AccessTokenInternal):
    query = sqlalchemy.dialects.postgresql.insert(AccessToken).values(
        **access_token.dict(),
    ).on_conflict_do_nothing(
        constraint='uq_accesstokens_token',
    )

    session = postgres.get_session()
    await session.execute(query)

    return access_token.dict()


async def token_store_refresh(refresh_token: schemas.RefreshTokenInternal):
    query = sqlalchemy.dialects.postgresql.insert(RefreshToken).values(
        **refresh_token.dict(),
    )

    session = postgres.get_session()
    await session.execute(query)

    return refresh_token.dict()


async def token_revoke_access(access_token: str):
    revoked_at = times.utcnow()

    query = sqlalchemy.update(AccessToken).where(
        AccessToken.token == access_token,
    ).values(is_revoked=True, revoked_at=revoked_at)

    session = postgres.get_session()
    return await session.execute(query)


async def token_revoke_access_all(client_id: int):
    revoked_at = times.utcnow()

    query = sqlalchemy.update(AccessToken).where(
        AccessToken.client_id == client_id,
    ).values(is_revoked=True, revoked_at=revoked_at)

    session = postgres.get_session()
    return await session.execute(query)


async def token_revoke_refresh(client_id: int):
    revoked_at = times.utcnow()

    query = sqlalchemy.update(RefreshToken).where(
        RefreshToken.client_id == client_id,
    ).values(is_revoked=True, revoked_at=revoked_at)

    session = postgres.get_session()
    return await session.execute(query)
