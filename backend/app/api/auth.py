import logging

import fastapi

from ..core import postgres
from . import exceptions
from . import models
from . import schemas
from . import security


TokenTypeHint = schemas.TokenTypeHint
logger = logging.getLogger(__name__)


class AuthCredentialsError(Exception):
    """Raises when wrong user credentials were provided"""


class TokenRefreshError(Exception):
    """Raises when provided access tokens are invalid"""


class TokenRevocationError(Exception):
    """Raises when provided token was already revoked or is not present"""


async def authenticate_user(email: str, password: str):
    """Authenticates the user with its credentials within the system."""
    auth_credentials_error = AuthCredentialsError(
        'Wrong user credentials were provided')

    user = await models.user_get_by_email(email.lower())

    if not user:
        raise auth_credentials_error

    if not security.verify_password(password, user['password']):
        raise auth_credentials_error

    return user


async def get_current_user(
    token: str = fastapi.Security(security.oauth2_scheme),
) -> schemas.UserCurrent:
    """Get currently authorized user."""
    unauthenticated_exception = exceptions.HTTPUnauthenticatedException(
        'Could not validate credentials',
    )

    client_id = security.extract_client_id_from_signed_token(token)

    if client_id is None:
        raise unauthenticated_exception

    logger.debug(f'{token = }')
    stored_access_token = await models.token_get_access(token)
    logger.debug(f'{stored_access_token = }')

    if not stored_access_token:
        raise unauthenticated_exception

    user = await models.user_get(client_id)
    logger.debug(f'{user = }')

    if user is None:
        raise unauthenticated_exception

    return schemas.UserCurrent(**user.__dict__)


async def obtain_token(user_id: int):
    """Obtain new auth token."""

    issued_access_token = security.issue_access_token(user_id=user_id)

    await models.token_store_access(issued_access_token)

    refresh_token = await models.token_get_refresh_by_client_id(user_id)

    if refresh_token is None:
        issued_refresh_token = security.issue_refresh_token(user_id=user_id)

        await models.token_store_refresh(issued_refresh_token)

        refresh_token = issued_refresh_token.dict()

    return schemas.TokenGet(
        user_id=user_id,
        access_token=issued_access_token.token,
        refresh_token=refresh_token['token'],
        expires_in=issued_access_token.expires_in,
        token_type=issued_access_token.token_type,
    )


async def refresh_token(client_id: int, access_token: str, refresh_token: str):
    """Refresh previously obtained token."""

    token_refresh_error = TokenRefreshError('Invalid token was provided')

    stored_access_token = await models.token_get_access(access_token)
    if not stored_access_token:
        raise token_refresh_error

    effective_client_id = security.extract_client_id_from_signed_token(access_token)
    if effective_client_id != client_id:
        raise token_refresh_error

    stored_refresh_token = await models.token_get_refresh_by_client_id(client_id)
    if not stored_refresh_token:
        raise token_refresh_error

    if stored_refresh_token['token'] != refresh_token:
        raise token_refresh_error

    new_access_token = security.issue_access_token(user_id=client_id)
    await models.token_store_access(new_access_token)

    return schemas.TokenGet(
        access_token=new_access_token.token,
        refresh_token=stored_refresh_token['token'],
        expires_in=new_access_token.expires_in,
        token_type=new_access_token.token_type,
    )


async def revoke_access_token(client_id: int, access_token: str):
    """Revoke access token."""

    token_revoke_error = TokenRevocationError('Access token revocation error')

    stored_access_token = await models.token_get_access(access_token)
    if not stored_access_token:
        raise token_revoke_error

    effective_client_id = security.extract_client_id_from_signed_token(access_token)
    if effective_client_id != client_id:
        raise token_revoke_error

    await models.token_revoke_access(access_token)


async def revoke_refresh_token(client_id: int):
    """Revoke user's refresh token and all access tokens."""

    async with postgres.get_session().transaction():
        await models.token_revoke_refresh(client_id)
        await models.token_revoke_access_all(client_id)


async def revoke_token(token: str, token_type_hint: str, client_id: int):
    """If access token was provided, revokes it. If refresh token was provided,
    revokes it and all the corresponding access tokens."""

    if token_type_hint == TokenTypeHint.ACCESS_TOKEN:
        return await revoke_access_token(client_id=client_id, access_token=token)
    elif token_type_hint == TokenTypeHint.REFRESH_TOKEN:
        return await revoke_refresh_token(client_id=client_id)

    access_token = await models.token_get_access(access_token=token)
    if access_token:
        return await revoke_access_token(client_id=client_id, access_token=token)

    refresh_token = await models.token_get_refresh(token)
    if refresh_token and refresh_token['client_id'] == client_id:
        return await revoke_refresh_token(client_id=client_id)

    raise TokenRevocationError('Invalid token type')
