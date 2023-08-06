import base64
import builtins
import inspect
import types

from .constants import TYPE, UNNECESSARY_CODE_TYPES, UNNECESSARY_DUNDER, UNNECESSARY_TYPES
from .help_funcs import get_class, is_iterable



class Encoder:

    @classmethod
    def encode(cls, obj):
        if isinstance(obj, bool | int | float | str | None):
            return obj
        elif isinstance(obj, list):
            return type(obj)((cls.encode(item) for item in obj))
        elif isinstance(obj, tuple | set | frozenset):
            return dict(__type=type(obj).__name__.lower(), data=[cls.encode(item) for item in obj])
        elif isinstance(obj, dict):
            return {key: cls.encode(value) for key, value in obj.items()}
        elif isinstance(obj, types.FunctionType | types.MethodType):
            return cls._func_encode(obj)
        elif isinstance(obj, types.CodeType):
            attrs = [attributes for attributes in dir(obj) if attributes.startswith("co")]
            data = {attr: cls.encode(getattr(obj, attr)) for attr in attrs if attr not in
                    UNNECESSARY_CODE_TYPES}
            return dict(__type=TYPE.CODE, data=data)
        elif isinstance(obj, types.CellType):
            return dict(__type=TYPE.CELL, data=cls.encode(obj.cell_contents))
        elif isinstance(obj, types.ModuleType):
            return dict(__type=TYPE.MODULE, data=obj.__name__)
        elif isinstance(obj, bytes):
            return dict(__type=TYPE.BYTES, data=base64.b64encode(obj).decode("ascii"))
        elif isinstance(obj, type):
            return cls._class_encode(obj)
        elif isinstance(obj, property):
            data = dict(fget=cls.encode(obj.fget), fset=cls.encode(obj.fset), fdel=cls.encode(obj.fdel))
            return dict(__type=TYPE.PROPERTY, data=data)
        elif is_iterable(obj):
            return dict(__type=TYPE.ITERATOR, data=list(map(cls.encode, obj)))
        elif isinstance(obj, object):
            return cls._object_encode(obj)

    @classmethod
    def decode(cls, obj):
        if isinstance(obj, list):
            return [cls.decode(element) for element in obj]
        elif isinstance(obj, dict):
            obj_type = obj.get("__type")

            if obj_type is None:
                return {key: cls.decode(val) for key, val in obj.items()}
            elif obj_type in (TYPE.TUPLE, TYPE.SET, TYPE.FROZENSET):
                data = obj.get("data")
                collection = getattr(builtins, obj.get("__type").lower())
                return collection((cls.decode(item) for item in data))
            elif obj_type == TYPE.FUNCTION:
                return cls._get_func(obj)
            elif obj_type == TYPE.CELL:
                return cls._get_cell(obj.get("data"))
            elif obj_type == TYPE.CODE:
                return cls._get_code(obj)
            elif obj_type == TYPE.MODULE:
                return __import__(obj.get("data"))
            elif obj_type == TYPE.BYTES:
                return base64.b64decode(obj.get("data").encode("ascii"))
            elif obj_type == TYPE.CLASS:
                return cls._get_class(obj)
            elif obj_type == TYPE.PROPERTY:
                data = cls.decode(obj.get("data"))
                return property(**data)
            elif obj_type == TYPE.OBJECT:
                return cls._get_object(obj)
            elif obj_type == TYPE.ITERATOR:
                return iter(cls.decode(value) for value in obj.get("data"))

        return obj

    @classmethod
    def _func_encode(cls, obj):
        fclass = get_class(obj)
        closure = (tuple(cell for cell in obj.__closure__ if cell.cell_contents is not fclass)
                   if obj.__closure__ is not None
                   else tuple())
        globs = {
            key: cls.encode(value)
            for (key, value) in obj.__globals__.items()
            if key in obj.__code__.co_names
               and value is not fclass
               and key != obj.__code__.co_name
        }

        function = cls.encode(dict(
            code=obj.__code__,
            name=obj.__name__,
            argdefs=obj.__defaults__,
            closure=closure,
            fdict=obj.__dict__,
            globals=globs,
        ))
        return dict(__type=TYPE.FUNCTION, data=function, is_method=isinstance(obj, types.MethodType))

    @classmethod
    def _class_encode(cls, obj):
        data = {
            attr: cls.encode(getattr(obj, attr))
            for attr, value in inspect.getmembers(obj)
            if attr not in UNNECESSARY_DUNDER
               and type(value) not in UNNECESSARY_TYPES
        }

        data["__bases__"] = [
            cls.encode(base) for base in obj.__bases__ if base != object
        ]
        data["__name__"] = obj.__name__
        return dict(__type=TYPE.CLASS, data=data)

    @classmethod
    def _object_encode(cls, obj):
        data = {
            "__class__": cls.encode(obj.__class__),
            "attrs": {
                attr: cls.encode(value)
                for (attr, value) in inspect.getmembers(obj)
                if not attr.startswith("__")
                   and not isinstance(value, types.FunctionType)
                   and not isinstance(value, types.MethodType)
            },
        }
        return dict(__type=TYPE.OBJECT, data=data)

    @classmethod
    def _get_func(cls, obj):
        func = cls.decode(obj.get("data"))
        fdict = func.pop("fdict")
        result = types.FunctionType(**func)
        result.__dict__.update(fdict)
        result.__globals__.update({result.__name__: result})
        return result

    @classmethod
    def _get_code(cls, obj):
        def f():
            pass

        code_dict = cls.decode(obj.get("data"))
        return f.__code__.replace(**code_dict)

    @classmethod
    def _get_class(cls, obj):
        data = obj.get("data")

        class_bases = tuple(cls.decode(base) for base in data.pop("__bases__"))
        class_dict = {
            attr: cls.decode(value)
            for (attr, value) in data.items()
            if not (isinstance(value, dict) and value.get("__type") == TYPE.FUNCTION)
        }

        result = type(data["__name__"], class_bases, class_dict)
        for key, value in data.items():
            if isinstance(value, dict) and value.get("__type") == TYPE.FUNCTION:
                try:
                    func = cls.decode(value)
                except ValueError:
                    closure = value.get("data")["closure"]
                    closure.get("data").append((lambda: result).__closure__[0])
                    func = cls.decode(value)

                func.__globals__.update({result.__name__: result})

                if value.get("is_method"):
                    func = types.MethodType(func, result)

                setattr(result, key, func)

        return result

    @classmethod
    def _get_object(cls, obj):
        data = obj.get("data")
        obj_class = cls.decode(data["__class__"])
        result = object.__new__(obj_class)
        result.__dict__ = {
            key: cls.decode(value) for key, value in data["attrs"].items()
        }
        return result

    @classmethod
    def _get_cell(cls, value):
        decoded = cls.decode(value)
        return (lambda: decoded).__closure__[0]

