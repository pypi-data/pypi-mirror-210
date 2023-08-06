from ._module_py import *
import typing

def configure_logging() -> None: ...

class _MangledName:
    UNICODE_LEFT_BRACKET: str
    UNICODE_RIGHT_BRACKET: str
    UNICODE_COMMA: str
    UNICODE_PERIOD: str
    @staticmethod
    def mangle(name: str) -> str: ...
    @staticmethod
    def demangle(name: str) -> str: ...
    @staticmethod
    def module_getattr(*, module_name: str, module_globals: typing.Mapping[str, typing.Any], name: str) -> typing.Any: ...

def pretty_class_name(cls, *, use_qualname: bool = ...) -> str: ...
