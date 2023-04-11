import typing

import fastapi

from ... import controllers
from ... import responses
from ... import schemas


router = fastapi.APIRouter()


@router.get(
    '/dummies',
    summary='Get a list of dummies',
    response_model=schemas.DummyList,
    response_description='List of dummies',
    responses=responses.gen_responses([
        responses.APIResponseNotFound,
        responses.APIResponseTemprorarilyUnavailable,
    ]),
)
async def get_dummies(
    quantity: int,
    with_name: bool = False,
    name: typing.Optional[str] = None,
):
    """Get a list of dummies.

    TEST API.
    """
    return await controllers.dummy_list(
        quantity,
        with_name=with_name,
        name=name,
    )
