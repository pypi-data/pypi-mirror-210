import types

BASIC_TYPES = {"int": int, "float": float, "str": str, "bool": bool, "complex": complex}

SEQUENCE_TYPES = {"list": list, "tuple": tuple}

SET_TYPES = {"set": set, "frozenset": frozenset}

BINARY_SEQUENCE_TYPES = {"bytes": bytes, "bytearray": bytearray}

MAPPING_TYPES = {"dict": dict}

SAME_SEQUENCE_TYPES = {"list": list, "tuple": tuple, "frozenset": frozenset, "set": set, "bytes": bytes,
                       "bytearray": bytearray}

ALL_COLLECTIONS_TYPES = {"list": list, "tuple": tuple, "frozenset": frozenset, "set": set, "bytes": bytes,
                         "bytearray": bytearray, "dict": dict}

CODE_PROPERTIES = (
    "co_argcount", "co_posonlyargcount", "co_kwonlyargcount", "co_nlocals",
    "co_stacksize", "co_flags", "co_code", "co_consts", "co_names", "co_varnames",
    "co_filename", "co_name", "co_firstlineno", "co_lnotab", "co_freevars", "co_cellvars"
)

CLASS_PROPERTIES = (
    "__name__",
    "__base__",
    "__basicsize__",
    "__dictoffset__",
    "__class__"
)

ITERABLE_TYPE = "iterator"

TYPES = (
    types.WrapperDescriptorType,
    types.MethodDescriptorType,
    types.BuiltinFunctionType,
    types.GetSetDescriptorType,
    types.MappingProxyType
)

DECORATOR_METHODS = {"staticmethod": staticmethod, "classmethod": classmethod}

