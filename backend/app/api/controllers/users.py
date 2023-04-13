from .. import responses
from .. import models
from .. import schemas
from .. import exceptions


class UserInvalidDataStatus(responses.Status):
    USER_INVALID_DATA = 'user_invalid_data'


class UserInvalidResponse(responses.APIResponseBadRequest):
    status: UserInvalidDataStatus


async def user_create(user: schemas.UserRegistration):
    try:
        return await models.user_create(user)
    except models.user.UserAlreadyExists as e:
        raise exceptions.HTTPBadRequestException(
            'User with such email or password already exists',
            status=UserInvalidDataStatus.USER_INVALID_DATA,
        ) from e
