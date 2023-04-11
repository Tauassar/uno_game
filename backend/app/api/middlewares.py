import abc
import dataclasses
import typing

import fastapi
import fastapi.responses
import pydantic
import starlette.middleware.base
import starlette.requests
import starlette.responses
import starlette.routing
import starlette.status
import starlette.types


@dataclasses.dataclass
class RequestMeta:
    """Instance created per request."""

    method: str
    path: str
    request: starlette.requests.Request
    response: typing.Optional[typing.Any]
    error: typing.Optional[BaseException]
    code: typing.Optional[int]
    options: dict


class Middleware(
    starlette.middleware.base.BaseHTTPMiddleware,
    metaclass=abc.ABCMeta,
):
    @abc.abstractmethod
    async def on_request(self, request_meta: RequestMeta):
        """Called before processing request."""

    @abc.abstractmethod
    async def on_response(self, request_meta: RequestMeta):
        """Called after request is processed, may contain errors."""

    def _get_base_route(self, request: starlette.requests.Request) -> str:
        """Find corresponding route for given request."""
        for route in request.app.routes:
            match, child_scope = route.matches(request.scope)
            if match == starlette.routing.Match.FULL:
                return route.path
        return request.url.path

    async def dispatch(
        self,
        request: starlette.requests.Request,
        call_next: typing.Callable,
    ):
        request_meta = RequestMeta(
            method=request.method,
            path=self._get_base_route(request),
            request=request,
            response=None,
            error=None,
            code=None,
            options={},
        )

        await self.on_request(request_meta)

        try:
            response = await call_next(request)
        except Exception as e:
            request_meta.error = e
            request_meta.code = starlette.status.HTTP_500_INTERNAL_SERVER_ERROR
            raise
        else:
            request_meta.response = response
            request_meta.code = response.status_code
        finally:
            await self.on_response(request_meta)
        return response


def get_client_ip(headers: typing.Dict):
    if 'X-Real-Ip' in headers:
        client_ip = headers.get('X-Real-Ip')
    elif 'X-Forwarded-For' in headers:
        client_ip = headers.get('X-Forwarded-For').split(',')[0]
    else:
        return None

    try:
        pydantic.IPvAnyAddress.validate(client_ip)
    except pydantic.errors.IPvAnyAddressError:
        client_ip = None

    return client_ip


class ClientIPMiddleware(starlette.middleware.base.BaseHTTPMiddleware):
    async def dispatch(
        self, request: fastapi.Request, call_next: typing.Callable,
    ) -> fastapi.responses.StreamingResponse:
        request.state.client_ip = get_client_ip(request.headers)

        return await call_next(request)
