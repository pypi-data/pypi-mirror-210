import inspect
from collections.abc import Iterable
from .utilities import get_class, get_cell, is_func
from .constants import PRIMITIVE_TYPES, DEFAULT_COLLECTIONS, ITERATOR_TYPE, BYTES_TYPE, FUNCTION_TYPE, MODULE_TYPE, \
    CELL_TYPE, IGNORE_CODE, CODE_TYPE, IGNORE_TYPES, IGNORE_DUNDER, CLASS_TYPE, OBJECT_TYPE, TUPLE_TYPE, SET_TYPE

from types import ModuleType, CellType, FunctionType, \
    MethodType, CodeType


class Converter:
    def convert(self, obj):
        if isinstance(obj, PRIMITIVE_TYPES):
            return obj
        elif isinstance(obj, ModuleType):
            return self._convert_module(obj)
        elif isinstance(obj, CellType):
            return self._convert_cell(obj)
        elif isinstance(obj, bytes):
            return self._convert_bytes(obj)
        elif isinstance(obj, DEFAULT_COLLECTIONS):
            return self._convert_collection(obj)
        elif isinstance(obj, Iterable):  # test
            return self._convert_iterable(obj)
        elif is_func(obj):
            return self._convert_function(obj)
        elif inspect.isclass(obj):
            return self._convert_class(obj)
        elif isinstance(obj, CodeType):
            return self._convert_code(obj)
        elif isinstance(obj, object):
            return self._convert_object(obj)
        else:
            raise Exception('Given type is not supported')

    def deconvert(self, obj):
        if isinstance(obj, PRIMITIVE_TYPES):
            return obj
        if isinstance(obj, list):
            return [self.deconvert(item) for item in obj]
        if isinstance(obj, dict):
            if '__type__' in obj.keys():
                type = obj['__type__']

                # if type is None:
                #     return {key: self.deconvert(value) for key, value in obj.items()}
                if type == BYTES_TYPE:
                    return self._deconvert_bytes(obj)
                if type == FUNCTION_TYPE:
                    return self._deconvert_function(obj)
                if type == ITERATOR_TYPE:
                    return self._deconvert_iterator(obj)
                if type == CELL_TYPE:
                    return self._deconvert_cell(obj)
                if type == CLASS_TYPE:
                    return self._deconvert_class(obj)
                if type == CODE_TYPE:
                    return self._deconvert_code(obj)
                if type == MODULE_TYPE:
                    return self._deconvert_module(obj)
                if type == OBJECT_TYPE:
                    return self._deconvert_object(obj)
                if type in (TUPLE_TYPE, SET_TYPE):
                    return self._deconvert_collection(obj, type)

            else:
                return {key: self.deconvert(value) for key, value in obj.items()}
        else:
            return obj

    def _deconvert_bytes(self, obj):
        return bytes.fromhex(obj['__data__'])

    def _deconvert_iterator(self, obj):
        return iter(self.deconvert(item) for item in obj['__data__'])

    def _deconvert_collection(self, obj, type):
        if type == 'tuple':
            return tuple((self.deconvert(item) for item in obj['__data__']))
        else:
            return set((self.deconvert(item) for item in obj['__data__']))

    def _deconvert_code(self, obj):
        def temp():
            pass

        return temp.__code__.replace(**(self.deconvert(obj['__data__'])))  # unpacking

    def _deconvert_module(self, obj):
        return __import__(obj['__data__'])

    def _deconvert_cell(self, obj):
        return get_cell(self.deconvert(obj['__data__']))

    def _deconvert_class(self, obj):
        data = obj['__data__']
        bases = tuple(self.deconvert(base) for base in data.pop('__bases__'))

        content = {}
        for key, value in data.items():
            if not (isinstance(value, dict) and '__type__' in value.keys() and value['__type__'] == FUNCTION_TYPE):
                content[key] = self.deconvert(value)

        new_class = type(data['__name__'], bases, content)

        for key, value in data.items():
            if isinstance(value, dict) and '__type__' in value.keys() and value['__type__'] == FUNCTION_TYPE:
                try:
                    func = self.deconvert(value)
                except ValueError:
                    closure = value['__data__']['closure']
                    closure['__data__'].append(get_cell(new_class))
                    func = self.deconvert(value)

                func.__globals__.update({new_class.__name__: new_class})

                if value['__method__']:
                    func = MethodType(func, new_class)

                setattr(new_class, key, func)

        return new_class

    def _deconvert_function(self, obj):
        deconverted_function = self.deconvert(obj['__data__'])

        dictionary = deconverted_function.pop('dictionary')
        new_function = FunctionType(**deconverted_function)
        # if obj['__method__'] and self.processed_class_obj != None:
        #     skeleton_func = MethodType(new_function, self.processed_class_obj)

        new_function.__dict__.update(dictionary)
        new_function.__globals__.update({new_function.__name__: new_function})
        return new_function

    def _deconvert_object(self, obj):
        data = obj['__data__']
        object_class = self.deconvert(data['__class__'])
        new_obj = object.__new__(object_class)
        # self.processed_class_obj = new_obj
        new_obj.__dict__ = {key: self.deconvert(value) for key, value in data['attrs'].items()}
        # self.processed_class_obj = None
        return new_obj

    def _convert_collection(self, obj):
        if isinstance(obj, dict):
            return {key: self.convert(value) for key, value in obj.items()}
        if isinstance(obj, list):
            return [self.convert(item) for item in obj]
        else:
            return {
                '__type__': type(obj).__name__,
                '__data__': [self.convert(item) for item in obj]
            }

    def _convert_bytes(self, obj):
        return {
            '__type__': BYTES_TYPE,
            '__data__': obj.hex()  # convert bytes to hex string
        }

    def _convert_iterable(self, obj):
        return {
            '__type__': ITERATOR_TYPE,
            '__data__': [self.convert(item) for item in obj]
        }

    def _convert_function(self, obj):
        class_name = get_class(obj)

        globs = {}
        for key, value in obj.__globals__.items():
            # __globals__ get all accessible from function global variables
            # __code__ provides access to function bytecode, co_names is tuple containing the names used by the bytecode
            # co_name - function name
            if key in obj.__code__.co_names and key != obj.__code__.co_name and value is not class_name:
                globs[key] = self.convert(value)

        # “Cell” objects are used to implement variables referenced by multiple scopes.
        # __closure__ stores tuple of closures like a cell objects
        closure = tuple()
        if obj.__closure__ is not None:
            closure = tuple(cell for cell in obj.__closure__ if cell.cell_contents is not class_name)

        return {
            '__type__': FUNCTION_TYPE,
            '__data__': self.convert(
                dict(
                    code=obj.__code__,
                    globals=globs,
                    name=obj.__name__,
                    argdefs=obj.__defaults__,  # A tuple containing defaults for argument with def values
                    closure=closure,
                    dictionary=obj.__dict__  # Dictionary of function attributes
                )
            ),
            '__method__': isinstance(obj, MethodType)  # or inspect.ismethod(obj)
        }

    def _convert_class(self, obj):

        # getmembers: Return all the members of an object in a list of (name, value) pairs sorted by name.
        data = {
            attr: self.convert(value)
            for attr, value in inspect.getmembers(obj)
            if attr not in IGNORE_DUNDER and type(value) not in IGNORE_TYPES
        }

        # get list of base classes exclude object
        data["__bases__"] = [
            self.convert(base) for base in obj.__bases__ if base != object
        ]

        data["__name__"] = obj.__name__

        return {
            '__type__': CLASS_TYPE,
            '__data__': data
        }

    def _convert_module(self, obj):
        return {
            '__type__': MODULE_TYPE,
            '__data__': obj.__name__
        }

    def _convert_cell(self, obj):
        return {
            '__type__': CELL_TYPE,
            '__data__': self.convert(obj.cell_contents)
        }

    def _convert_code(self, obj):

        attrs = [attr for attr in dir(obj) if attr.startswith('co')]

        return {
            '__type__': CODE_TYPE,
            '__data__': {attr: self.convert(getattr(obj, attr)) for attr in attrs if
                         attr not in IGNORE_CODE}
        }

    def _convert_object(self, obj):
        data = {
            '__class__': self.convert(obj.__class__),
            'attrs': {
                attr: self.convert(value) for attr, value in inspect.getmembers(obj)
                if not attr.startswith('__') and not is_func(value)
            }
        }

        return {
            '__type__': OBJECT_TYPE,
            '__data__': data
        }
