from types import NoneType, FunctionType, CodeType, CellType, MethodType
import inspect
import builtins
from serializer_Konchik.constants import (PRIMITIVES, COLLECTIONS, CODE_ATTRIBUTES,
                                          TYPE, VALUE, METHOD_DECORATORS, ITERATOR_TYPE)


class Unpacker:

    @staticmethod
    def unpack(obj: dict):
        """
        Method that converts dictionary that
        represents the object to object.

        Parameters:
        obj (Any): Dictionary.

        Returns:
        object.
        """

        if obj[TYPE] in tuple(map(lambda p: p.__name__, PRIMITIVES)):
            if obj[TYPE] == str(NoneType.__name__):
                return None
            else:
                return getattr(builtins, obj[TYPE])(obj[VALUE])

        if obj[TYPE] in tuple(map(lambda c: c.__name__, COLLECTIONS)):
            if obj[TYPE] == dict.__name__:
                return {Unpacker.unpack(item[0]): Unpacker.unpack(item[1])
                        for item in obj[VALUE]}
            else:
                return getattr(builtins, obj[TYPE])(Unpacker.unpack(item)
                                                    for item in obj[VALUE])

        if obj[TYPE] in [FunctionType.__name__, MethodType.__name__]:
            return Unpacker._unpack_function(obj[VALUE])

        if obj[TYPE] == CodeType.__name__:
            return Unpacker._unpack_code(obj[VALUE])

        if obj[TYPE] == CellType.__name__:
            return CellType(Unpacker.unpack(obj[VALUE]))

        if obj[TYPE] == "class":
            return Unpacker._unpack_class(obj[VALUE])

        if obj[TYPE] in tuple(map(lambda md: md.__name__, METHOD_DECORATORS)):
            return getattr(builtins, obj[TYPE])(Unpacker.unpack(obj[VALUE]))

        if obj[TYPE] == property.__name__:
            return property(fget=Unpacker.unpack(obj[VALUE]["fget"]),
                            fset=Unpacker.unpack(obj[VALUE]["fset"]),
                            fdel=Unpacker.unpack(obj[VALUE]["fdel"]))

        if obj[TYPE] == ITERATOR_TYPE:
            return iter(Unpacker.unpack(item) for item in obj[VALUE])

        return Unpacker._unpack_object(obj[VALUE])

    @staticmethod
    def _unpack_function(obj: dict):
        code = Unpacker._unpack_code(obj["__code__"])

        globs = Unpacker._unpack_globals(obj["__globals__"], obj)
        globs["builtins"] = __import__("builtins")

        closure = Unpacker.unpack(obj["__closure__"])
        closure = tuple(closure) if closure else tuple()

        unpacked = FunctionType(code=code, globals=globs, closure=closure)
        unpacked.__globals__.update({unpacked.__name__: unpacked})
        unpacked.__defaults__ = Unpacker.unpack(obj["__defaults__"])
        unpacked.__kwdefaults__ = Unpacker.unpack(obj["__kwdefaults__"])

        return unpacked

    @staticmethod
    def _unpack_globals(globs, func):
        unpacked = dict()

        for key, value in globs.items():
            if "module" in key:
                unpacked[value[VALUE]] = __import__(value[VALUE])

            elif value != func["__name__"]:
                unpacked[key] = Unpacker.unpack(value)

        return unpacked

    @staticmethod
    def _unpack_class(obj):

        attrs = {member: Unpacker.unpack(value)
                 for member, value in obj.items()}

        cls = type(Unpacker.unpack(obj["__name__"]),
                   Unpacker.unpack(obj["__bases__"]),
                   attrs)

        for value in attrs.values():
            if inspect.isfunction(value):
                value.__globals__.update({cls.__name__: cls})
            elif isinstance(value, (staticmethod, classmethod)):
                value.__func__.__globals__.update({cls.__name__: cls})

        return cls

    @staticmethod
    def _unpack_object(obj):

        unpacked = object.__new__(Unpacker.unpack(obj["__class__"]))
        unpacked.__dict__ = {key: Unpacker.unpack(value)
                             for key, value in obj["__vars__"].items()}

        return unpacked

    @staticmethod
    def _unpack_code(code):
        return CodeType(*(Unpacker.unpack(code[ATTRIBUTE])
                          for ATTRIBUTE in CODE_ATTRIBUTES))

        # return CodeType(Unpacker.unpack(code["co_argcount"]),
        #                 Unpacker.unpack(code["co_posonlyargcount"]),
        #                 Unpacker.unpack(code["co_kwonlyargcount"]),
        #                 Unpacker.unpack(code["co_nlocals"]),
        #                 Unpacker.unpack(code["co_stacksize"]),
        #                 Unpacker.unpack(code["co_flags"]),
        #                 Unpacker.unpack(code["co_code"]),
        #                 Unpacker.unpack(code["co_consts"]),
        #                 Unpacker.unpack(code["co_names"]),
        #                 Unpacker.unpack(code["co_varnames"]),
        #                 Unpacker.unpack(code["co_filename"]),
        #                 Unpacker.unpack(code["co_name"]),
        #                 Unpacker.unpack(code["co_qualname"]),
        #                 Unpacker.unpack(code["co_firstlineno"]),
        #                 Unpacker.unpack(code["co_lnotab"]),
        #                 Unpacker.unpack(code["co_exceptiontable"]),
        #                 Unpacker.unpack(code["co_freevars"]),
        #                 Unpacker.unpack(code["co_cellvars"]))
