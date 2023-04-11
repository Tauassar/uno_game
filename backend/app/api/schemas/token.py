import datetime
import enum
import typing

import pydantic


class TokenTypeHint(str, enum.Enum):
    ACCESS_TOKEN = 'access_token'
    REFRESH_TOKEN = 'refresh_token'

    def __str__(self):
        return str(self.value)


class TokenGet(pydantic.BaseModel):
    access_token: pydantic.constr(strict=True, max_length=255)
    refresh_token: pydantic.constr(strict=True, max_length=127)
    token_type: pydantic.constr(strict=True, regex='bearer')  # noqa: F821
    expires_in: pydantic.StrictInt

    class Config:
        extra = 'forbid'


class TokenBase(pydantic.BaseModel):
    token: pydantic.constr(strict=True, max_length=255)
    token_type: pydantic.constr(strict=True, regex='bearer')  # noqa: F821

    class Config:
        extra = 'forbid'


class TokenInternalInfo(pydantic.BaseModel):
    is_revoked: pydantic.StrictBool = False
    issued_at: datetime.datetime
    revoked_at: typing.Optional[datetime.datetime] = None
    client_id: pydantic.StrictInt

    class Config:
        extra = 'forbid'


class AccessTokenInternal(TokenBase, TokenInternalInfo):
    expires_in: pydantic.StrictInt

    class Config:
        extra = 'forbid'


class RefreshTokenInternal(TokenBase, TokenInternalInfo):
    class Config:
        extra = 'forbid'
