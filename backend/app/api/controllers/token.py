from .. import auth
from .. import exceptions
from .. import responses
from .. import schemas


class TokenObtainUnauthenticatedStatus(responses.Status):
    TOKEN_INVALID_CREDENTIALS = 'token_invalid_credentials'


class TokenRefreshBadRequestStatus(responses.Status):
    TOKEN_REFRESH_ERROR = 'token_refresh_error'


class TokenRevokeBadRequestStatus(responses.Status):
    TOKEN_REVOKE_ERROR = 'token_revoke_error'


class TokenObtainAPIResponseUnauthenticated(responses.APIResponseUnauthenticated):
    status: TokenObtainUnauthenticatedStatus


class TokenRefreshAPIResponseBadRequest(responses.APIResponseBadRequest):
    status: TokenRefreshBadRequestStatus


class TokenRevokeAPIResponseBadRequest(responses.APIResponseBadRequest):
    status: TokenRevokeBadRequestStatus


async def token_obtain(email: str, password: str, client_ip: str):
    try:
        user = await auth.authenticate_user(email, password)
    except auth.AuthCredentialsError as e:
        raise exceptions.HTTPUnauthenticatedException(
            'Could not authenticate user with provided credentials',
            status=TokenObtainUnauthenticatedStatus.TOKEN_INVALID_CREDENTIALS,
        ) from e

    return await auth.obtain_token(user['id'])


async def token_refresh(
    current_user: schemas.UserCurrent,
    access_token: str,
    refresh_token: str,
):
    try:
        return await auth.refresh_token(current_user.id, access_token, refresh_token)
    except auth.TokenRefreshError as e:
        raise exceptions.HTTPBadRequestException(
            detail='Token refresh error',
            status=TokenRefreshBadRequestStatus.TOKEN_REFRESH_ERROR,
        ) from e


async def token_revoke(
    current_user: schemas.UserCurrent,
    token: str,
    token_type_hint: str,
):
    try:
        await auth.revoke_token(token, token_type_hint, current_user.id)
    except auth.TokenRevocationError as e:
        raise exceptions.HTTPBadRequestException(
            detail='Token revoke error',
            status=TokenRevokeBadRequestStatus.TOKEN_REVOKE_ERROR,
        ) from e
