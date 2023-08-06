import types
import inspect
import re
from serializer.constants import BASIC_TYPES, SET_TYPES, SEQUENCE_TYPES, \
    BINARY_SEQUENCE_TYPES, SAME_SEQUENCE_TYPES, MAPPING_TYPES, ALL_COLLECTIONS_TYPES, \
    CODE_PROPERTIES, CLASS_PROPERTIES, TYPES, DECORATOR_METHODS, ITERABLE_TYPE


class Serializer:

    @staticmethod
    def get_object_type(obj) -> str:
        """
            Get_object_type returns the object type as a string.

            :param obj: the object whose type you want to find out.
            :type obj: object
         """
        return re.search(r"\'(\w+)\'", str(type(obj)))[1]

    def serialize(self, obj):
        """
            Serialize, a method that serializes any python object.

            :param obj: the object you want to serialize.
            :type obj: object
         """
        # Serialization of basic types.
        if isinstance(obj, tuple(BASIC_TYPES.values())):
            return self.__serialize_basic_types__(obj)

        elif isinstance(obj, property):
            return self.__serialize_property(obj)

        elif Serializer.is_iterator(obj):
            return self.__serialize_iterator(obj)

        # Serialization None type.
        elif isinstance(obj, types.NoneType):
            return self.__serialize_none_type__()

        # Serialization of same sequence types.
        # [ list, tuple, frozenset, set, bytes, bytearray ].
        elif isinstance(obj, tuple(SAME_SEQUENCE_TYPES.values())):
            return self.__serialize_same_sequence_types__(obj)

        # Serialization of mapping types.
        # [ dict ]
        elif isinstance(obj, tuple(MAPPING_TYPES.values())):
            return self.__serialize_mapping_types__(obj)

        # Serialization function.
        elif inspect.isfunction(obj):
            return self.__serialize_function__(obj)

        # Serialization code.
        elif inspect.iscode(obj):
            return self.__serialize_code__(obj)

        # Serialization cell.
        elif isinstance(obj, types.CellType):
            return self.__serialize_cell__(obj)

        # Serialization class.
        elif inspect.isclass(obj):
            return self.__serialize_class__(obj)

        else:
            return self.__serialize_object__(obj)

    @staticmethod
    def is_iterator(obj):
        """
            is_iterator, a method that checks whether the object belongs to the iterator type.

            :param obj: the object that you trust..
            :type obj: object
         """
        return hasattr(obj, '__iter__') and hasattr(obj, '__next__') and callable(obj.__iter__)

    def __serialize_basic_types__(self, obj):
        serialize_result = dict()
        serialize_result["type"] = self.get_object_type(obj)
        serialize_result["value"] = obj if not isinstance(obj, complex) else str(obj)
        return serialize_result

    def __serialize_property(self, obj):
        serialize_result = dict()
        serialize_result["type"] = type(obj).__name__
        serialize_result["value"] = {"fget": self.serialize(obj.fget),
                                     "fset": self.serialize(obj.fset),
                                     "fdel": self.serialize(obj.fdel)}
        return serialize_result

    def __serialize_iterator(self, obj):
        serialize_result = dict()
        serialize_result["type"] = ITERABLE_TYPE
        serialize_result["value"] = list(map(self.serialize, obj))
        return serialize_result

    def __serialize_none_type__(self):
        serialize_result = dict()
        serialize_result["type"] = "NoneType"
        # serialize_result["value"] = "definitely none"
        serialize_result["value"] = "None"
        return serialize_result

    def __serialize_same_sequence_types__(self, obj):
        serialize_result = dict()
        serialize_result["type"] = Serializer.get_object_type(obj)
        serialize_result["value"] = [self.serialize(item) for item in obj]
        return serialize_result

    def __serialize_mapping_types__(self, obj):
        serialize_result = dict()
        serialize_result["type"] = Serializer.get_object_type(obj)
        serialize_result["value"] = [[self.serialize(key), self.serialize(value)] for (key, value) in obj.items()]
        return serialize_result

    def __serialize_function__(self, obj):
        serialize_result = dict()
        serialize_result["type"] = "function"
        serialize_result["value"] = self.__total_func_serialize__(obj)
        return serialize_result

    def __total_func_serialize__(self, obj, cls=None):
        value = dict()
        value["__name__"] = obj.__name__
        value["__globals__"] = self.__get_globals__(obj, cls)
        value["__closure__"] = self.serialize(obj.__closure__)
        value["__defaults__"] = self.serialize(obj.__defaults__)
        value["__kwdefaults__"] = self.serialize(obj.__kwdefaults__)
        value["__code__"] = {key: self.serialize(value) for key, value in inspect.getmembers(obj.__code__)
                             if key in CODE_PROPERTIES}
        return value

    def __get_globals__(self, obj, cls=None):
        """Work with __globals__ and __code__"""

        globs = dict()
        for global_variable in obj.__code__.co_names:

            if global_variable in obj.__globals__:

                # That prop is module.
                if isinstance(obj.__globals__[global_variable], types.ModuleType):
                    globs[" ".join(["module", global_variable])] = self.serialize(
                        obj.__globals__[global_variable].__name__)

                # That prop is class.
                elif inspect.isclass(obj.__globals__[global_variable]):

                    if cls and obj.__globals__[global_variable] != cls or not cls:
                        globs[global_variable] = self.serialize(obj.__globals__[global_variable])

                elif global_variable != obj.__code__.co_name:
                    globs[global_variable] = self.serialize(obj.__globals__[global_variable])

                # It works out once in order to avoid recursion (serialization of itself).
                else:
                    globs[global_variable] = self.serialize(obj.__name__)

        return globs

    def __serialize_code__(self, obj):
        serialize_result = dict()
        serialize_result["type"] = "code"
        serialize_result["value"] = {key: self.serialize(value) for key, value in inspect.getmembers(obj)
                                     if key in CODE_PROPERTIES}
        return serialize_result

    def __serialize_cell__(self, obj):
        serialize_result = dict()
        serialize_result["type"] = "cell"
        serialize_result["value"] = self.serialize(obj.cell_contents)
        return serialize_result

    def __serialize_class__(self, obj):
        serialize_result = dict()
        serialize_result["type"] = "class"
        serialize_result["value"] = self.__total_class_serialize__(obj)
        return serialize_result

    def __total_class_serialize__(self, obj):
        serialize_result = dict()
        serialize_result["__name__"] = self.serialize(obj.__name__)

        for key, value in obj.__dict__.items():

            if key in CLASS_PROPERTIES or type(value) in TYPES:
                continue

            if isinstance(obj.__dict__[key], staticmethod):
                serialize_result[key] = dict()
                serialize_result[key]["type"] = "staticmethod"
                serialize_result[key]["value"] = {
                    "type": "function", "value": self.__total_func_serialize__(value.__func__, obj)
                }

            elif isinstance(obj.__dict__[key], classmethod):
                serialize_result[key] = dict()
                serialize_result[key]["type"] = "classmethod"
                serialize_result[key]["value"] = {
                    "type": "function", "value": self.__total_func_serialize__(value.__func__, obj)
                }

            elif inspect.ismethod(value):
                serialize_result[key] = self.__total_func_serialize__(value.__func__, obj)

            elif inspect.isfunction(value):
                serialize_result[key] = dict()
                serialize_result[key]["type"] = "function"
                serialize_result[key]["value"] = self.__total_func_serialize__(value, obj)

            else:
                serialize_result[key] = self.serialize(value)

        serialize_result["__bases__"] = dict()
        serialize_result["__bases__"]["type"] = "tuple"
        serialize_result["__bases__"]["value"] = [self.serialize(base) for base in obj.__bases__ if base != object]

        return serialize_result

    def __serialize_object__(self, obj):
        serialize_result = dict()
        serialize_result["type"] = "object"
        serialize_result["value"] = self.__total_object_serialization__(obj)
        return serialize_result

    def __total_object_serialization__(self, obj):
        value = dict()
        value["__class__"] = self.serialize(obj.__class__)
        value["__members__"] = {key: self.serialize(value) for key, value in inspect.getmembers(obj)
                                if not (key.startswith("__") or inspect.isfunction(value) or inspect.ismethod(value))}
        return value

    def deserialize(self, obj):
        """
            deserialize, a method that deserializes any python object.

            :param obj: the object you want to deserialize.
            :type obj: object
        """

        if obj["type"] in self.extract_keys(str(BASIC_TYPES.keys())):
            return self.__deserialize_basic_types__(obj)

        elif obj["type"] == property.__name__:
            return self.__deserialize_property(obj)

        elif obj["type"] == ITERABLE_TYPE:
            return self.__deserialize_iterator(obj)

        elif obj["type"] in str(SAME_SEQUENCE_TYPES.keys()):
            return self.__deserialize_collections__(obj)

        elif obj["type"] == "code":
            return self.__deserialize_code__(obj["value"])

        elif obj["type"] == "function":
            return self.__deserialize_function__(obj["value"])

        elif obj["type"] == "cell":
            return self.__deserialize_cell__(obj)

        elif obj["type"] == "class":
            return self.__deserialize_class__(obj["value"])

        elif obj["type"] in DECORATOR_METHODS:
            return DECORATOR_METHODS[obj["type"]](self.deserialize(obj["value"]))

        elif obj["type"] == "object":
            return self.__deserialize_object__(obj["value"])

    def __deserialize_iterator(self, obj):
        return iter(self.deserialize(item) for item in obj["value"])

    def __deserialize_property(self, obj):
        return property(fget=self.deserialize(obj["value"]["fget"]),
                        fset=self.deserialize(obj["value"]["fset"]),
                        fdel=self.deserialize(obj["value"]["fdel"]))

    def __deserialize_basic_types__(self, obj):
        if obj["type"] == bool.__name__:
            return obj["value"]
        return BASIC_TYPES[obj["type"]](obj["value"])

    def __deserialize_collections__(self, obj):
        collection_type = obj["type"]

        if collection_type in SAME_SEQUENCE_TYPES.keys():
            return SAME_SEQUENCE_TYPES[collection_type](self.deserialize(item) for item in obj["value"])

        elif collection_type in ALL_COLLECTIONS_TYPES.keys():
            return ALL_COLLECTIONS_TYPES[collection_type](
                {self.deserialize(item[0]): self.deserialize(item[1]) for item in obj["value"]})

    def __deserialize_code__(self, code):
        return types.CodeType(*(self.deserialize(code[prop]) for prop in CODE_PROPERTIES))

    def __deserialize_function__(self, func):
        code = func["__code__"]
        globs = func["__globals__"]
        func_closure = func["__closure__"]
        des_globals = self.__deserialize_globals__(globs, func)

        cl = self.deserialize(func_closure)
        if cl:
            closure = tuple(cl)
        else:
            closure = tuple()
        codeType = self.__deserialize_code__(code)

        des_globals["__builtins__"] = __import__("builtins")
        des_function = types.FunctionType(code=codeType, globals=des_globals, closure=closure)
        des_function.__globals__.update({des_function.__name__: des_function})

        des_function.__defaults__ = self.deserialize(func["__defaults__"])
        des_function.__kwdefaults__ = self.deserialize(func["__kwdefaults__"])

        return des_function

    def __deserialize_globals__(self, globs, func):
        des_globals = dict()

        for glob in globs:
            if "module" in glob:
                des_globals[globs[glob]["value"]] = __import__(globs[glob]["value"])

            elif globs[glob] != func["__name__"]:
                des_globals[glob] = self.deserialize(globs[glob])

        return des_globals

    def __deserialize_cell__(self, obj):
        return types.CellType(self.deserialize(obj["value"]))

    def __deserialize_class__(self, obj):
        bases = self.deserialize(obj["__bases__"])

        members = {member: self.deserialize(value) for member, value in obj.items()}

        cls = type(self.deserialize(obj["__name__"]), bases, members)

        for k, member in members.items():
            if inspect.isfunction(member):
                member.__globals__.update({cls.__name__: cls})
            elif isinstance(member, (staticmethod, classmethod)):
                member.__func__.__globals__.update({cls.__name__: cls})

        return cls

    def __deserialize_object__(self, obj):
        cls = self.deserialize(obj["__class__"])
        des = object.__new__(cls)
        des.__dict__ = {key: self.deserialize(value) for key, value in obj["__members__"].items()}
        return des

    # def(BASIC_TYPES) -> return  str: [ int, float, complex, ... ]
    @staticmethod
    def extract_keys(string) -> str:
        return re.search(r"\[.*\]", string).group()
