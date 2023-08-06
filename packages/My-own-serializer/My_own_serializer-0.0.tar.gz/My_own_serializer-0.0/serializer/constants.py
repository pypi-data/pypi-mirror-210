import types
from enum import Enum

# KEY WORDS
TYPE = "type"
SOURCE = "source"

CODE = "__code__"
GLOBALS = types.FunctionType.__globals__.__name__
NAME = "__name__"
DEFAULTS = "__defaults__"
CLOSURE = types.FunctionType.__closure__.__name__

BASES = "__bases__"
DICT = "__dict__"

CLASS = "__class__"
OBJECT = "object"


CODE_PROPERTIES = [prop.__name__ for prop in [
    types.CodeType.co_argcount,
    types.CodeType.co_posonlyargcount,
    types.CodeType.co_kwonlyargcount,
    types.CodeType.co_nlocals,
    types.CodeType.co_stacksize,
    types.CodeType.co_flags,
    types.CodeType.co_code,
    types.CodeType.co_consts,
    types.CodeType.co_names,
    types.CodeType.co_varnames,
    types.CodeType.co_filename,
    types.CodeType.co_name,
    types.CodeType.co_firstlineno,
    types.CodeType.co_lnotab,
    types.CodeType.co_freevars,
    types.CodeType.co_cellvars]
]


UNIQUE_TYPES = [
    types.MappingProxyType,
    types.WrapperDescriptorType,
    types.MemberDescriptorType,
    types.GetSetDescriptorType,
    types.BuiltinFunctionType
]

# JSON

INF_LITERAL = str(1E1000)
NAN_LITERAL = str(1E1000 / 1E1000)

TRUE_LITERAL = "true"
FALSE_LITERAL = "false"

NULL_LITERAL = "null"

INT_PATTERN = fr"[+-]?\d+"
FLOAT_PATTERN = fr"(?:[+-]?\d+(?:\.\d+)?(?:e[+-]?\d+)?|[+-]?{INF_LITERAL}\b|{NAN_LITERAL}\b)"
BOOL_PATTERN = fr"({TRUE_LITERAL}|{FALSE_LITERAL})\b"
STRING_PATTERN = fr"\"(?:(?:\\\")|[^\"])*\""
NULL_PATTERN = fr"\b{NULL_LITERAL}\b"

ELEMENTARY_TYPES_PATTERN = fr"{FLOAT_PATTERN}|{INT_PATTERN}|{BOOL_PATTERN}|{STRING_PATTERN}|{NULL_PATTERN}"

# This regex use recursive statements to be able to capture nested lists and objects.
ARRAY_PATTERN = r"\[(?R)?(?:,(?R))*\]"
OBJECT_PATTERN = r"\{(?:(?R):(?R))?(?:,(?R):(?R))*\}"

VALUE_PATTERN = fr"\s*({ELEMENTARY_TYPES_PATTERN}|" + \
                fr"{ARRAY_PATTERN}|{OBJECT_PATTERN})\s*"


# XML 

KEY_GROUP_NAME = "key"
VALUE_GROUP_NAME = "value"

XML_SCHEME_SOURCE = "xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" " + \
                    "xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\""

XML_SCHEME_PATTERN = "xmlns:xsi=\"http://www\.w3\.org/2001/XMLSchema-instance\" " + \
    "xmlns:xsd=\"http://www\.w3\.org/2001/XMLSchema\""

ELEMENTARY_NAMES_PATTERN = "int|float|bool|str|NoneType|list|dict"

XML_ELEMENT_PATTERN = fr"(\<(?P<{KEY_GROUP_NAME}>{ELEMENTARY_NAMES_PATTERN})\>" + \
    fr"(?P<{VALUE_GROUP_NAME}>([^<>]*)|(?R)+)\</(?:{ELEMENTARY_NAMES_PATTERN})\>)"

FIRST_XML_ELEMENT_PATTERN = fr"(\<(?P<{KEY_GROUP_NAME}>{ELEMENTARY_NAMES_PATTERN})\s*({XML_SCHEME_PATTERN})?\>" + \
                            fr"(?P<{VALUE_GROUP_NAME}>([^<>]*)|(?R)+)\</(?:{ELEMENTARY_NAMES_PATTERN})\>)"


# ENUM FOR 
class Serializer(Enum):
    Json = 1,
    Xml = 2
