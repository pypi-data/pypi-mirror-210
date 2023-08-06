from types import NoneType, EllipsisType, WrapperDescriptorType, MethodDescriptorType, BuiltinFunctionType, \
    MappingProxyType, GetSetDescriptorType

PRIMITIVE_TYPES = (int, float, complex, str, bool, NoneType, EllipsisType)
DEFAULT_COLLECTIONS = (list, set, dict, tuple)
ITERATOR_TYPE = 'iterator'
BYTES_TYPE = 'bytes'
FUNCTION_TYPE = 'function'
MODULE_TYPE = 'module'
CELL_TYPE = 'cell'
CODE_TYPE = 'code'
CLASS_TYPE = 'class'
OBJECT_TYPE = 'object'
TUPLE_TYPE = 'tuple'
SET_TYPE = 'set'
IGNORE_DUNDER = (
    "__mro__",
    "__doc__",
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
    "__objclass__"
)

IGNORE_TYPES = (
    WrapperDescriptorType,
    MethodDescriptorType,
    BuiltinFunctionType,
    MappingProxyType,
    GetSetDescriptorType,
)

IGNORE_CODE = (
    "co_positions",
    "co_lines",
    "co_exceptiontable",
    "co_lnotab",
)
