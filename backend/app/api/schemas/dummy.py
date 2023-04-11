import typing

import pydantic


class Pong(pydantic.BaseModel):
    id: pydantic.StrictInt
    name: typing.Optional[pydantic.StrictStr]


class DummyList(pydantic.BaseModel):
    dummies: list[Pong]
