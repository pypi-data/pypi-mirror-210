from enum import StrEnum, auto
import types


class TYPE(StrEnum):
    TUPLE = auto()
    SET = auto()
    FROZENSET = auto()
    FUNCTION = auto()
    CODE = auto()
    CELL = auto()
    MODULE = auto()
    BYTES = auto()
    CLASS = auto()
    PROPERTY = auto()
    OBJECT = auto()
    ITERATOR = auto()


UNNECESSARY_CODE_TYPES = (
    "co_positions",
    "co_lines",
    "co_exceptiontable",
    "co_lnotab",
)

UNNECESSARY_DUNDER = (
    "__mro__",
    "__base__",
    "__basicsize__",
    "__class__",
    "__dictoffset__",
    "__name__",
    "__qualname__",
    "__text_signature__",
    "__itemsize__",
    "__flags__",
    "__weakrefoffset__",
    "__objclass__",
)

UNNECESSARY_TYPES = (
    types.WrapperDescriptorType,
    types.MethodDescriptorType,
    types.BuiltinFunctionType,
    types.MappingProxyType,
    types.GetSetDescriptorType,
)

