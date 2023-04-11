import enum
import typing

import fastapi.routing
import pydantic


class Status(str, enum.Enum):
    @classmethod
    def get_status_string_values(cls) -> typing.List[str]:
        return [status.value for status in cls]


class NoContentStatus(Status):
    NO_CONTENT = 'no_content'


class BadRequestStatus(Status):
    BAD_REQUEST = 'bad_request'


class UnauthenticatedStatus(Status):
    UNAUTHENTICATED = 'unauthenticated'


class PaymentRequiredStatus(Status):
    PAYMENT_REQUIRED = 'payment_required'


class UnauthorizedStatus(Status):
    UNAUTHORIZED = 'unauthorized'


class NotFoundStatus(Status):
    NOT_FOUND = 'not_found'


class TooManyRequestsStatus(Status):
    TOO_MANY_REQUESTS = 'too_many_requests'


class InternalErrorStatus(Status):
    INTERNAL_ERROR = 'internal_error'


class TemporarilyUnavailableStatus(Status):
    TEMPORARILY_UNAVAILABLE = 'temporarily_unavailable'


class APIResponse(pydantic.BaseModel):
    status: Status
    status_code: int
    detail: str

    class Config:
        schema_extra = {
            'required': ['status', 'status_code', 'detail'],
        }

    @pydantic.validator('status_code')
    def _validate_status_code(cls, value: int) -> int:  # noqa: N805
        if not (200 <= value <= 599):
            raise ValueError('Invalid status code. Should be in range of 200 and 599')

        return value

    @classmethod
    def get_status_code(cls) -> int:
        return cls.__fields__['status_code'].default

    @classmethod
    def generate_schema(cls) -> typing.Dict:
        return {
            'application/json': {
                'example': {
                    'detail': 'string',
                    'status': {
                        'type': 'string',
                        'enum': cls.__fields__['status'].type_.get_status_string_values(),
                    },
                    'status_code': {
                        'type': 'int',
                        'default': cls.get_status_code(),
                    },
                },
            },
        }


class APIResponseOctetStream:

    @classmethod
    def get_status_code(cls) -> int:
        return 200

    @classmethod
    def get_content(cls) -> dict:
        return {'application/octet-stream': {}}


class APIResponseNoContent(APIResponse):
    status: NoContentStatus = NoContentStatus.NO_CONTENT
    status_code: int = 204


class APIResponseBadRequest(APIResponse):
    status: BadRequestStatus = BadRequestStatus.BAD_REQUEST
    status_code: int = 400


class APIResponseUnauthenticated(APIResponse):
    status: UnauthenticatedStatus = UnauthenticatedStatus.UNAUTHENTICATED
    status_code: int = 401


class APIResponsePaymentRequired(APIResponse):
    status: PaymentRequiredStatus = PaymentRequiredStatus.PAYMENT_REQUIRED
    status_code: int = 402


class APIResponseUnauthorized(APIResponse):
    status: UnauthorizedStatus = UnauthorizedStatus.UNAUTHORIZED
    status_code: int = 403


class APIResponseNotFound(APIResponse):
    status: NotFoundStatus = NotFoundStatus.NOT_FOUND
    status_code: int = 404


class APIResponseTooManyRequests(APIResponse):
    status: TooManyRequestsStatus = TooManyRequestsStatus.TOO_MANY_REQUESTS
    status_code: int = 429


class APIResponseInternalError(APIResponse):
    status: InternalErrorStatus = InternalErrorStatus.INTERNAL_ERROR
    status_code: int = 500


class APIResponseTemprorarilyUnavailable(APIResponse):
    status: TemporarilyUnavailableStatus = (
        TemporarilyUnavailableStatus.TEMPORARILY_UNAVAILABLE
    )
    status_code: int = 503


def gen_responses(statuses):
    responses = {}

    for status in statuses:
        if issubclass(status, APIResponseOctetStream):
            responses[status.get_status_code()] = {
                'content': status.get_content(),
            }
            continue

        if status.get_status_code() == 204:
            responses[204] = {}
            continue

        responses[status.get_status_code()] = {'model': status}

    return responses


def extend_route_with_schemas(route: fastapi.routing.APIRoute):
    # Since 500 status code with API schema has to be present for all endpoints,
    # add a corresponding API response for its model
    route.responses[500] = {'model': APIResponseInternalError}
    route.response_fields[500] = fastapi.routing.create_response_field(
        name=f'Response_{500}_{route.unique_id}',
        type_=APIResponseInternalError,
    )

    # Since response with 204 status code has no body, set its response model
    # to 'None'
    if 204 in route.responses:
        route.status_code = 204
        route.response_model = None

    # Since media-type of responses is application/json by default,
    # ensure that responses with 200 status code and octet-stream content type
    # has only the corresponding content type by indicating that its response class
    # is 'StreamingResponse'
    if (200 in route.responses and
            route.responses[200] == {'content': APIResponseOctetStream.get_content()}):
        route.status_code = 200
        route.response_class = fastapi.responses.StreamingResponse
