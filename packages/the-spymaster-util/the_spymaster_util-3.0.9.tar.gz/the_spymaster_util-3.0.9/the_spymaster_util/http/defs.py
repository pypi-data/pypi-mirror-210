from typing import Any, Dict, Iterable, Type, TypeVar, Union

from the_spymaster_util.http.errors import APIError

CONTEXT_HEADER_KEY = "x-spymaster-context"
CONTEXT_ID_HEADER_KEY = "x-spymaster-context-id"
JSONType = Union[str, int, float, bool, list, Dict[str, Any], None]
HTTPHeaders = Dict[str, str]
E = TypeVar("E", bound=APIError)
ErrorTypes = Iterable[Type[E]]
ErrorCodeMapping = Dict[str, Type[E]]
