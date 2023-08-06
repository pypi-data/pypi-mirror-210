import logging
from http import HTTPStatus
from typing import TYPE_CHECKING, Any, Optional

from the_spymaster_util.logger import get_context_id
from the_spymaster_util.strings import camel_to_const

if TYPE_CHECKING:
    from the_spymaster_util.http.defs import ErrorTypes

log = logging.getLogger(__name__)


class APIError(Exception):
    def __init__(
        self,
        *,
        message: str,
        http_status: HTTPStatus,
        context_id: Optional[str] = None,
        data: Optional[dict] = None,
        **kwargs,
    ):
        self.message = message
        self.http_status = http_status
        self.context_id = context_id
        self.data = data or {}
        self.kwargs = kwargs
        super().__init__(message)

    @classmethod
    def get_error_code(cls) -> str:
        return camel_to_const(cls.__name__)

    @property
    def status_code(self) -> int:
        return self.http_status.value

    @property
    def response_payload(self) -> dict:
        return {
            "message": self.message,
            "error_code": self.get_error_code(),
            "context_id": self.context_id or get_context_id(),
            "data": self.data,
        }

    def __getitem__(self, item: str) -> Any:
        return self.data.get(item)

    def __getattr__(self, item: str) -> Any:
        return self[item]

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, APIError):
            return False
        return (
            self.message == other.message
            and self.http_status == other.http_status
            and self.data == other.data
            and self.get_error_code() == other.get_error_code()
        )

    def __str__(self) -> str:
        return f"{self.get_error_code()}: {self.message}"


class InternalServerError(APIError):
    def __init__(
        self,
        *,
        message: str = "Internal server error",
        http_status: HTTPStatus = HTTPStatus.INTERNAL_SERVER_ERROR,
        data: Optional[dict] = None,
        **kwargs,
    ):
        super().__init__(message=message, http_status=http_status, data=data, **kwargs)


class BadRequestError(APIError):
    def __init__(
        self,
        *,
        message: str,
        http_status: HTTPStatus = HTTPStatus.BAD_REQUEST,
        data: Optional[dict] = None,
        **kwargs,
    ):
        super().__init__(message=message, http_status=http_status, data=data, **kwargs)


class UnauthenticatedError(BadRequestError):
    def __init__(
        self,
        *,
        message: str,
        http_status: HTTPStatus = HTTPStatus.UNAUTHORIZED,
        data: Optional[dict] = None,
        **kwargs,
    ):
        super().__init__(message=message, http_status=http_status, data=data, **kwargs)


class ForbiddenError(BadRequestError):
    def __init__(
        self,
        *,
        message: str,
        http_status: HTTPStatus = HTTPStatus.FORBIDDEN,
        data: Optional[dict] = None,
        **kwargs,
    ):
        super().__init__(message=message, http_status=http_status, data=data, **kwargs)


class NotFoundError(BadRequestError):
    def __init__(
        self,
        *,
        message: str,
        http_status: HTTPStatus = HTTPStatus.NOT_FOUND,
        data: Optional[dict] = None,
        **kwargs,
    ):
        super().__init__(message=message, http_status=http_status, data=data, **kwargs)


DEFAULT_ERRORS: "ErrorTypes" = frozenset(
    {APIError, InternalServerError, BadRequestError, UnauthenticatedError, ForbiddenError, NotFoundError}
)
