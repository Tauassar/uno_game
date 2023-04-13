import fastapi.security.oauth2

from ... import controllers
from ... import responses
from ... import schemas


router = fastapi.APIRouter()


@router.post(
    '/register',
    summary='Register new user',
    response_model=schemas.UserGet,
    response_description='User registered',
    responses=responses.gen_responses([controllers.UserInvalidResponse]),
)
async def register(
    user_data: schemas.UserRegistration,
):
    """Register new user:

    - `phone`: Mobile phone number
    - `email`: Provide username
    - `password`: Provide user password

    The following status codes are defined for 401 response:

    * `token_invalid_credentials` - Invalid credentials were provided
    """

    return await controllers.user_create(user_data)
