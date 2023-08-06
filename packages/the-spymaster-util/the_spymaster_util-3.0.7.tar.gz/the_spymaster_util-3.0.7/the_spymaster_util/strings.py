import re
from typing import TypeVar

CAMEL_TO_CONST_1 = re.compile(r"(.)([A-Z][a-z]+)")
CAMEL_TO_CONST_2 = re.compile(r"([a-z0-9])([A-Z])")
T = TypeVar("T")


def camel_to_const(string: str) -> str:
    string = CAMEL_TO_CONST_1.sub(r"\1_\2", string)
    return CAMEL_TO_CONST_2.sub(r"\1_\2", string).upper()
