import typing

import fastapi
import fastapi.security.oauth2

from ... import auth
from ... import controllers
from ... import responses
from ... import schemas
from ... import security


router = fastapi.APIRouter()


@router.post(
    '/token',
    summary='Obtain OAuth2 token',
    response_model=schemas.TokenGet,
    response_description='Obtained token',
    responses=responses.gen_responses([controllers.TokenObtainAPIResponseUnauthenticated]),
)
async def obtain_token(
    request: fastapi.Request,
    form_data: fastapi.security.oauth2.OAuth2PasswordRequestFormStrict = fastapi.Depends(),
):
    """Obtain `OAuth2` token by providing valid user credentials:

    - `grant_type`: Must always be set to 'password'
    - `username`: Provide username
    - `password`: Provide user password

    Obtained `access_token` may be later used to access protected resources,
    use appropriate `HTTP` header:

    ```
    Authorization: Bearer obtained_access_token
    ```

    The following status codes are defined for 401 response:

    * `token_invalid_credentials` - Invalid credentials were provided
    """

    return await controllers.token_obtain(
        email=form_data.username,
        password=form_data.password,
        client_ip=request.state.client_ip,
    )


@router.post(
    '/token/refresh',
    summary='Refresh OAuth2 token',
    response_model=schemas.TokenGet,
    response_description='Refreshed token',
    responses=responses.gen_responses([controllers.TokenRefreshAPIResponseBadRequest]),
)
async def refresh_token(
    grant_type: str = fastapi.Form(..., regex='refresh_token'),
    refresh_token: str = fastapi.Form(...),
    access_token: str = fastapi.Security(security.oauth2_scheme),
    current_user: schemas.UserCurrent = fastapi.Security(auth.get_current_user),
):
    """Refresh `OAuth2` access token by providing valid refresh token:

    - `grant_type`: Must always be set to 'refresh_token'
    - `refresh_token`: Valid refresh token

    Obtained `access_token` may be later used to access protected resources,
    use appropriate `HTTP` header:

    ```
    Authorization: Bearer obtained_access_token
    ```

    The following status codes are defined for 400 response:

    * `token_refresh_error` - Any error related to token refreshing
    """

    return await controllers.token_refresh(
        current_user=current_user,
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post(
    '/token/revoke',
    summary='Revoke OAuth2 token',
    response_description='Token revoked successfully',
    responses=responses.gen_responses([
        responses.APIResponseNoContent,
        controllers.TokenRevokeAPIResponseBadRequest,
    ]),
    status_code=204,
    response_class=fastapi.Response,
)
async def revoke_token(
    token: str = fastapi.Form(...),
    token_type_hint: typing.Optional[schemas.TokenTypeHint] = fastapi.Form(None),
    access_token: str = fastapi.Security(security.oauth2_scheme),
    current_user: schemas.UserCurrent = fastapi.Security(auth.get_current_user),
):
    """Revoke `OAuth2` token by providing revocable token:

    - `token`: Revocable token (access or refresh token)
    - `token_type_hint`: Used to specify which token type is going to be revoked. If not set,
    this will be determined automatically.

    If access token was provided, revokes it. If refresh token was provided,
    revokes it and all the corresponding access tokens.

    The following status codes are defined for 400 response:

    * `token_revoke_error` - Any error related to token revocation
    """

    await controllers.token_revoke(
        current_user=current_user,
        token=token,
        token_type_hint=token_type_hint,
    )
