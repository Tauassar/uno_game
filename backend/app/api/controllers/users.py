from .. import responses
from .. import models
from .. import schemas
from .. import exceptions


class UserInvalidDataStatus(responses.Status):
    USER_INVALID_DATA = 'user_invalid_data'


async def user_create(user: schemas.UserCreate):
    try:
        user = await models.user_create(user)
    except models.user.UserEmailAlreadyInUse as e:
        raise exceptions.HTTPUnauthenticatedException(
            'Could not authenticate user with provided credentials',
            status=UserInvalidDataStatus.USER_INVALID_DATA,
        ) from e
