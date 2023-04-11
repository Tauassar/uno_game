import typing

import starlette.exceptions
import starlette.status

from . import responses


class HTTPException(starlette.exceptions.HTTPException):
    def __init__(
        self,
        status_code: int,
        detail: str,
        status: responses.Status,
    ):
        super().__init__(status_code, detail=detail)

        self.status = status


class HTTPUnauthenticatedException(HTTPException):
    """Raises on unauthenticated access."""

    def __init__(
        self,
        detail: str = 'Unauthenticated access',
        status: responses.Status = responses.UnauthenticatedStatus.UNAUTHENTICATED,
    ):
        super().__init__(starlette.status.HTTP_401_UNAUTHORIZED, detail, status=status)

        self.headers = {'WWW-Authenticate': 'Bearer'}


class HTTPUnauthorizedException(HTTPException):
    """Raises on unauthorized access."""

    def __init__(
        self,
        detail: str = 'Unauthorized access',
        perms: typing.Optional[typing.List[str]] = None,
        status: responses.Status = responses.UnauthorizedStatus.UNAUTHORIZED,
    ):
        if perms:
            detail = f'Unauthorized access. Needed perms: {perms!r}'

        super().__init__(starlette.status.HTTP_403_FORBIDDEN, detail, status=status)


class HTTPNotFoundException(HTTPException):
    """Raises when queried object was not found."""

    def __init__(
        self,
        detail: str = 'Queried object is not found',
        status: responses.Status = responses.NotFoundStatus.NOT_FOUND,
    ):
        super().__init__(starlette.status.HTTP_404_NOT_FOUND, detail, status=status)


class HTTPBadRequestException(HTTPException):
    """Raises when client made an invalid request."""

    def __init__(
        self,
        detail: str = 'Request is invalid',
        status: responses.Status = responses.BadRequestStatus.BAD_REQUEST,
    ):
        super().__init__(starlette.status.HTTP_400_BAD_REQUEST, detail, status=status)


class HTTPTooManyRequestsException(HTTPException):
    """Raises when client made too many requests."""

    def __init__(
        self,
        detail: str = 'Too many requests',
        status: responses.Status = responses.TooManyRequestsStatus.TOO_MANY_REQUESTS,
    ):
        super().__init__(starlette.status.HTTP_429_TOO_MANY_REQUESTS, detail, status=status)


class HTTPTemprorarilyUnavailableException(HTTPException):
    """Raises when tried to reach unavailable service."""

    def __init__(
        self,
        detail: str = 'Requested resource is unavailable',
        status: responses.Status = (
            responses.TemporarilyUnavailableStatus.TEMPORARILY_UNAVAILABLE
        ),
    ):
        super().__init__(starlette.status.HTTP_503_SERVICE_UNAVAILABLE, detail, status=status)


class HTTPNoContentException(HTTPException):
    """Raises when no response is provided."""

    def __init__(
        self,
        detail: str = 'No content',
        status: responses.Status = responses.NoContentStatus.NO_CONTENT,
    ):
        super().__init__(starlette.status.HTTP_204_NO_CONTENT, detail, status=status)


class HTTPPaymentRequired(HTTPException):
    """Raises when payment required."""

    def __init__(
        self,
        detail: str = 'Payment required',
        status: responses.Status = responses.PaymentRequiredStatus.PAYMENT_REQUIRED,
    ):
        super().__init__(
            starlette.status.HTTP_402_PAYMENT_REQUIRED,
            detail,
            status=status,
        )
