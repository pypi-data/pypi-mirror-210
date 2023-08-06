import inspect
from types import MethodType, FunctionType


def get_class(method):  # Get base class for method
    cls = getattr(inspect.getmodule(method), method.__qualname__.split(".<locals>", 1)[0].rsplit(".", 1)[0], None)
    if isinstance(cls, type):
        return cls


def get_cell(value):  # pack data to cell using closure mechanism
    x = value

    def closure():
        return x

    return closure.__closure__[0]


def is_func(value):
    return isinstance(value, MethodType) or isinstance(value, FunctionType)