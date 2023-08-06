from .constants import CODE_PROPERTIES, UNIQUE_TYPES, TYPE, SOURCE, CODE,\
    GLOBALS, NAME, DEFAULTS, CLOSURE, BASES, DICT, CLASS, OBJECT
import inspect
from types import NoneType, ModuleType, CodeType, FunctionType, CellType


class ObjectConverter:
    @classmethod
    def get_dict(cls, obj, is_inner_func=False):
        if type(obj) in (int, float, bool, str, NoneType):
            return obj

        if type(obj) is list:
            return [cls.get_dict(i) for i in obj]

        result = {TYPE: type(obj).__name__}

        if type(obj) is dict:
            result[SOURCE] = [[cls.get_dict(key), cls.get_dict(value)] for key, value in obj.items()]
            return result

        if type(obj) in (set, frozenset, tuple, bytes, bytearray):
            result[SOURCE] = cls.get_dict([*obj])
            return result

        if type(obj) is complex:
            result[SOURCE] = {complex.real.__name__: obj.real,
                              complex.imag.__name__: obj.imag}
            return result

        if type(obj) is ModuleType:
            # result[SOURCE] = obj.__name__
            # return result
            return {TYPE: ModuleType.__name__,
                    SOURCE: obj.__name__}

        if type(obj) is CodeType:
            result[SOURCE] = cls.__get_code_dict(obj)
            return result

        if type(obj) is CellType:
            result[SOURCE] = cls.get_dict(obj.cell_contents)
            return result

        if type(obj) in (staticmethod, classmethod):
            result[SOURCE] = cls.get_dict(obj.__func__, is_inner_func)
            return result

        if inspect.isroutine(obj):
            result[SOURCE] = cls.__get_routine_dict(obj, is_inner_func)
            return result

        elif inspect.isclass(obj):
            result[SOURCE] = cls.__get_class_dict(obj)
            return result

        else:
            result[SOURCE] = cls.__get_object_dict(obj)
            return result

    @classmethod
    def get_object(cls, dictionary, is_dict=False):
        if is_dict:
            return {cls.get_object(item[0]): cls.get_object(item[1]) for item in dictionary}

        if type(dictionary) not in (dict, list):
            return dictionary

        elif type(dictionary) is list:
            return [cls.get_object(o) for o in dictionary]

        else:
            object_type = dictionary[TYPE]
            object_source = dictionary[SOURCE]

            if object_type == dict.__name__:
                return cls.get_object(object_source, is_dict=True)

            cols_dict = {t.__name__: t for t in [
                set, frozenset, tuple, bytes, bytearray]}

            if object_type in cols_dict:
                return cols_dict[object_type](cls.get_object(object_source))

            if object_type == complex.__name__:
                return object_source[complex.real.__name__] + object_source[complex.imag.__name__] * 1j

            if object_type == ModuleType.__name__:
                return __import__(object_source)

            if object_type == CodeType.__name__:
                return CodeType(*[cls.get_object(object_source[prop]) for prop in CODE_PROPERTIES])

            if object_type == CellType.__name__:
                return CellType(cls.get_object(object_source))

            if object_type == staticmethod.__name__:
                return staticmethod(cls.get_object(object_source))

            if object_type == classmethod.__name__:
                return classmethod(cls.get_object(object_source))

            if object_type == FunctionType.__name__:
                return cls.__create_function(object_source)

            if object_type == type.__name__:
                return cls.__create_class(object_source)

            else:
                return cls.__create_object(object_source)

    @classmethod
    def __create_function(cls, object_source):
        code = cls.get_object(object_source[CODE])
        global_vars = cls.get_object(object_source[GLOBALS])
        name = cls.get_object(object_source[NAME])
        defaults = cls.get_object(object_source[DEFAULTS])
        closure = cls.get_object(object_source[CLOSURE])

        for key in global_vars:
            if key in code.co_name and key in globals():
                global_vars[key] = globals()[key]

        func = FunctionType(code, global_vars, name, defaults, closure)

        if func.__name__ in global_vars:
            func.__globals__.update({func.__name__: func})

        return func

    @classmethod
    def __create_class(cls, object_source):
        name = cls.get_object(object_source[NAME])
        bases = cls.get_object(object_source[BASES])
        dictionary = object_source[DICT]
        dictionary = {cls.get_object(key): cls.get_object(
            value) for key, value in dictionary.items()}

        cl = type(name, bases, dictionary)

        for attr in cl.__dict__.values():
            if inspect.isroutine(attr):
                if type(attr) in (staticmethod, classmethod):
                    fglobs = attr.__func__.__globals__
                else:
                    fglobs = attr.__globals__

                for gv in fglobs.keys():
                    if gv == cl.__name__:
                        fglobs[gv] = cl

        return cl

    @classmethod
    def __create_object(cls, object_source):
        cl = cls.get_object(object_source[CLASS])
        dictionary = object_source[DICT]
        dictionary = {cls.get_object(key): cls.get_object(
            value) for key, value in dictionary.items()}

        obj = object.__new__(cl)
        obj.__dict__ = dictionary

        return obj

    @classmethod
    def __get_code_dict(cls, obj):
        result = {}

        for key, value in inspect.getmembers(obj):
            if key in CODE_PROPERTIES:
                result[key] = cls.get_dict(value)

        return result

    @classmethod
    def __get_object_dict(cls, obj):
        result = {}

        # Class
        result[CLASS] = cls.get_dict(obj.__class__)

        # Dict
        result[DICT] = cls.__get_obj_dict(obj)

        return result

    @classmethod
    def __get_routine_dict(cls, obj, is_inner_func):
        result = {}

        # Code
        result[CODE] = cls.get_dict(obj.__code__)

        # Global vars
        global_vars = cls.__get_global_vars(obj, is_inner_func)
        result[GLOBALS] = cls.get_dict(global_vars)

        # Name
        result[NAME] = cls.get_dict(obj.__name__)

        # Defaults
        result[DEFAULTS] = cls.get_dict(obj.__defaults__)

        # Closure
        result[CLOSURE] = cls.get_dict(obj.__closure__)

        return result

    # @classmethod
    # def __get_global_vars(cls, func, is_inner_func):
    #     name = func.__name__
    #     global_vars = {}
    #
    #     for var_name in func.__code__.co_names:
    #         if var_name in func.__globals__:
    #             # Module
    #             if type(func.__globals__[var_name]) is ModuleType:
    #                 global_vars[var_name] = func.__globals__[var_name]
    #
    #             # Class
    #             elif inspect.isclass(func.__globals__[var_name]):
    #                 c = func.__globals__[var_name]
    #
    #                 if is_inner_func and name in c.__dict__ and func == c.__dict__[name].__func__:
    #                     global_vars[var_name] = c.__name__
    #                 else:
    #                     global_vars[var_name] = c
    #
    #             elif var_name == func.__code__.co_name:
    #                 global_vars[var_name] = func.__name__
    #
    #             else:
    #                 global_vars[var_name] = func.__globals__[var_name]
    #
    #     return global_vars

    @classmethod
    def __get_global_vars(cls, func, is_inner_func):
        name = func.__name__
        gvars = {}

        for gvar_name in func.__code__.co_names:
            # Separating the variables that the function needs
            if gvar_name in func.__globals__:

                # Module
                if type(func.__globals__[gvar_name]) is ModuleType:
                    gvars[gvar_name] = func.__globals__[gvar_name]

                # Class
                elif inspect.isclass(func.__globals__[gvar_name]):
                    # To prevent recursion, the class in which this method is declared is replaced with the
                    # name of the class. In the future, this name will be replaced by the class type
                    c = func.__globals__[gvar_name]
                    if is_inner_func and name in c.__dict__ and func == c.__dict__[name].__func__:  # !!!!
                        gvars[gvar_name] = c.__name__
                    else:
                        gvars[gvar_name] = c

                # Recursion protection
                elif gvar_name == func.__code__.co_name:
                    gvars[gvar_name] = func.__name__

                else:
                    gvars[gvar_name] = func.__globals__[gvar_name]

        return gvars

    @classmethod
    def __get_obj_dict(cls, obj):
        dictionary = {key: value for key, value in obj.__dict__.items()}
        dictionary2 = {}

        for key, value in dictionary.items():
            if type(value) not in UNIQUE_TYPES:
                if inspect.isroutine(value):
                    dictionary2[cls.get_dict(key)] = cls.get_dict(value, is_inner_func=True)
                else:
                    dictionary2[cls.get_dict(key)] = cls.get_dict(value)

        return dictionary2

    @classmethod
    def __get_class_dict(cls, obj):
        result = {}

        # Name
        result[NAME] = cls.get_dict(obj.__name__)

        # Bases
        result[BASES] = cls.get_dict(tuple(base for base in obj.__bases__ if base != object))

        # Dict
        result[DICT] = cls.__get_obj_dict(obj)

        return result
