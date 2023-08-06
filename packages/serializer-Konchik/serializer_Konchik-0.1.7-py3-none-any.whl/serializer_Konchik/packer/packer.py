import inspect
from typing import Any
from types import FunctionType, ModuleType, CellType
from serializer_Konchik.is_functions import is_iterable
from serializer_Konchik.constants import (PRIMITIVES, COLLECTIONS, CODE_ATTRIBUTES,
                                          TYPE, VALUE, ITERATOR_TYPE,
                                          IGNORED_CLASS_ATTRIBUTES, IGNORED_TYPES)


class Packer:

    @staticmethod
    def pack(obj: Any) -> dict:
        """
        Method that converts object to the dictionary
        that represents the object.

        Parameters:
        obj (Any): Any Python object.

        Returns:
        dictionary.
        """

        if isinstance(obj, PRIMITIVES):
            return {TYPE: type(obj).__name__,
                    VALUE: str(obj) if isinstance(obj, complex) else obj}

        if isinstance(obj, COLLECTIONS):
            if isinstance(obj, dict):
                return {TYPE: type(obj).__name__,
                        VALUE: [[Packer.pack(key), Packer.pack(value)]
                                for key, value in obj.items()]}
            else:
                return {TYPE: type(obj).__name__,
                        VALUE: [Packer.pack(item) for item in obj]}

        if inspect.isfunction(obj):
            return {TYPE: type(obj).__name__,
                    VALUE: Packer._pack_function(obj)}

        if inspect.iscode(obj):
            return {TYPE: type(obj).__name__,
                    VALUE: {key: Packer.pack(value)
                            for key, value in inspect.getmembers(obj)
                            if key in CODE_ATTRIBUTES}}

        if isinstance(obj, CellType):
            return {TYPE: type(obj).__name__,
                    VALUE: Packer.pack(obj.cell_contents)}

        if inspect.isclass(obj):
            return {TYPE: "class",
                    VALUE: Packer._pack_class(obj)}

        if isinstance(obj, property):
            return {TYPE: type(obj).__name__,
                    VALUE: {"fget": Packer.pack(obj.fget),
                            "fset": Packer.pack(obj.fset),
                            "fdel": Packer.pack(obj.fdel)}}

        if is_iterable(obj):
            return {TYPE: ITERATOR_TYPE,
                    VALUE: [Packer.pack(item) for item in obj]}

        # if inspect.isgenerator(obj):
        #     raise TypeError("Python does not support creating generators on the fly")

        if inspect.ismethod(obj):
            return {TYPE: type(obj).__name__,
                    VALUE: Packer._pack_function(obj.__func__)}

        return {TYPE: "object",
                VALUE: {"__class__": Packer.pack(obj.__class__),
                        "__vars__": {key: Packer.pack(value) for key, value in vars(obj).items()}}}

    @staticmethod
    def _pack_function(obj: FunctionType, cls=None):

        return {"__name__": obj.__name__,
                "__globals__": Packer._pack_globals(obj, cls),
                "__closure__": Packer.pack(obj.__closure__),
                "__defaults__": Packer.pack(obj.__defaults__),
                "__kwdefaults__": Packer.pack(obj.__kwdefaults__),
                "__code__": {key: Packer.pack(value)
                             for key, value in inspect.getmembers(obj.__code__)
                             if key in CODE_ATTRIBUTES}}

    @staticmethod
    def _pack_globals(obj, cls=None):
        globs = dict()

        for key, value in obj.__globals__.items():

            if key not in obj.__code__.co_names:
                continue

            if isinstance(value, ModuleType):
                globs[f"module {key}"] = Packer.pack(key)

            elif inspect.isclass(value):
                if cls and value != cls or not cls:
                    globs[key] = Packer.pack(value)

            elif key == obj.__code__.co_name:
                globs[key] = Packer.pack(obj.__name__)

            else:
                globs[key] = Packer.pack(value)

        return globs

    @staticmethod
    def _pack_class(obj):
        packed = dict()
        packed["__name__"] = Packer.pack(obj.__name__)

        for key, value in obj.__dict__.items():

            if key in IGNORED_CLASS_ATTRIBUTES or type(value) in IGNORED_TYPES:
                continue

            if isinstance(obj.__dict__[key], staticmethod):
                packed[key] = dict()
                packed[key]["type"] = "staticmethod"
                packed[key]["value"] = {"type": "function", "value": Packer._pack_function(value.__func__, obj)}

            elif isinstance(obj.__dict__[key], classmethod):
                packed[key] = dict()
                packed[key]["type"] = "classmethod"
                packed[key]["value"] = {"type": "function", "value": Packer._pack_function(value.__func__, obj)}

            elif inspect.ismethod(value):
                packed[key] = Packer._pack_function(value.__func__, obj)

            elif inspect.isfunction(value):
                packed[key] = dict()
                packed[key]["type"] = "function"
                packed[key]["value"] = Packer._pack_function(value, obj)

            else:
                packed[key] = Packer.pack(value)

        packed["__bases__"] = dict()
        packed["__bases__"]["type"] = "tuple"
        packed["__bases__"]["value"] = [Packer.pack(item) for item in obj.__bases__ if item != object]

        return packed
