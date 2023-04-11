import asyncio
import logging
import typing

import fastapi
import pydantic
import stringcase

from ..core import conf
from ..core import postgres
from . import exceptions
from . import middlewares
from . import responses
from . import v1


app = fastapi.FastAPI(
    title='UNO game backend',
    openapi_url='/api/v1/openapi.json',
    version='0.0.1',
)
app.include_router(v1.api_router, prefix='/api/v1')
app.add_middleware(middlewares.ClientIPMiddleware)


logger = logging.getLogger(__name__)


@app.get(
    '/',
    include_in_schema=False,
)
async def redirect_to_docs():
    return fastapi.responses.RedirectResponse(url=app.docs_url)


@app.on_event('startup')
async def startup():
    await postgres.connect(conf.postgres.uri)


async def _handle_service_exceptions(cls: typing.Type, coro):
    try:
        await coro
    except asyncio.CancelledError as e:
        logger.error(f'{cls.__name__!r} service was cancelled: {e!r}')
        raise e
    except Exception as e:
        logger.error(f'Exception raised in {cls.__name__!r} service: {e!r}')
        raise e


@app.on_event('shutdown')
async def shutdown():
    await postgres.disconnect()


@app.exception_handler(pydantic.ValidationError)
async def query_params_validation_error_handler(
    request: fastapi.Request, exc: pydantic.ValidationError,
) -> fastapi.responses.Response:
    """Handles pydantic validation errors.

    Without this handler, if query parameters are defined as pydantic model,
    a validation error would throw an internal error to client.
    """
    return fastapi.responses.JSONResponse(
        status_code=422,
        content={
            'detail': exc.errors(),
        },
    )


@app.exception_handler(exceptions.HTTPException)
async def request_exception_handler(request: fastapi.Request, exc: exceptions.HTTPException):
    return fastapi.responses.JSONResponse(
        status_code=exc.status_code,
        content={
            'detail': exc.detail,
            'status': exc.status,
            'status_code': exc.status_code,
        },
    )


@app.exception_handler(500)
async def internal_exception_handler(request: fastapi.Request, exc: Exception):
    return fastapi.responses.JSONResponse(
        status_code=500,
        content={
            'detail': 'Internal Server Error',
            'status': responses.InternalErrorStatus.INTERNAL_ERROR,
            'status_code': 500,
        },
    )


def enrich_openapi_schema(app: fastapi.FastAPI):
    operation_ids = []
    for route in app.routes:
        if isinstance(route, fastapi.routing.APIRoute):
            route.operation_id = stringcase.camelcase(route.name)
            operation_ids.append(route.operation_id)
            responses.extend_route_with_schemas(route)


enrich_openapi_schema(app)
