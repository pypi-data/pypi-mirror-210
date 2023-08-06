from typing import Final
from types import NoneType
import types
import enum

XML: Final[str] = "xml"
JSON: Final[str] = "json"

KEY: Final[str] = "key"
TYPE: Final[str] = "type"
VALUE: Final[str] = "value"

PRIMITIVES: Final[list] = (int, float, bool, str, NoneType, complex)
COLLECTIONS: Final[list] = (set, dict, list, tuple, bytes, bytearray)

CODE_ATTRIBUTES: Final[list] = ("co_argcount",
                                "co_posonlyargcount",
                                "co_kwonlyargcount",
                                "co_nlocals",
                                "co_stacksize",
                                "co_flags",
                                "co_code",
                                "co_consts",
                                "co_names",
                                "co_varnames",
                                "co_filename",
                                "co_name",
                                "co_qualname",
                                "co_firstlineno",
                                "co_lnotab",
                                "co_exceptiontable",
                                "co_freevars",
                                "co_cellvars")

IGNORED_CLASS_ATTRIBUTES: list[str] = ("__name__",
                                       "__base__",
                                       "__basicsize__",
                                       "__dictoffset__",
                                       "__class__")

IGNORED_TYPES: Final[list] = (types.WrapperDescriptorType,
                              types.MethodDescriptorType,
                              types.BuiltinFunctionType,
                              types.GetSetDescriptorType,
                              types.MappingProxyType)

METHOD_DECORATORS: Final[list] = (classmethod, staticmethod)

ITERATOR_TYPE: Final[str] = "iterator"


class JsonRegularExpression(enum.Enum):
    INT = r"[+-]?\d+"
    FLOAT = fr"({INT}(?:\.\d+)?(?:e{INT})?)"
    BOOL = r"((True)|(False))\b"
    STR = r"\"((\\\")|[^\"])*\""
    NONE = r"\b(None)\b"
    COMPLEX = fr"{FLOAT}{FLOAT}j"

    LIST_RECURSION = r"\[(?R)?(,(?R))*\]"
    DICT_RECURSION = r"\{((?R):(?R))?(?:,(?R):(?R))*\}"

    ANY_VALUE = fr"\s*({LIST_RECURSION}|" \
                fr"{DICT_RECURSION}|" \
                fr"{STR}|" \
                fr"{FLOAT}|" \
                fr"{BOOL}|" \
                fr"{INT}|" \
                fr"{NONE}|" \
                fr"{COMPLEX}\s*)"


class XmlRegularExpression(enum.Enum):
    TYPES = "|".join(map(lambda x: x.__name__, list(PRIMITIVES) + [list, dict]))
    ITEM = fr"\s*(\<(?P<{KEY}>{TYPES})\>(?P<{VALUE}>([^<>]*)|(?R)+)\</({TYPES})\>)\s*"
