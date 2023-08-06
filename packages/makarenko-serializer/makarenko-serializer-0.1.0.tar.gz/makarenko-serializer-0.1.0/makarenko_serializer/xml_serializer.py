from .encoder import Encoder
from .help_funcs import count_structs


class XmlSerializer:
    @classmethod
    def load(cls, file):
        return cls.loads(file.read())

    @classmethod
    def dump(cls, obj, file):
        file.write(cls.dumps(obj))

    @classmethod
    def dumps(cls, obj):
        return cls._dumps(Encoder.encode(obj))

    @classmethod
    def _dumps(cls, obj):
        if isinstance(obj, int | float | bool | str | None):
            obj_type = type(obj).__name__
            if obj_type not in ("int", "float", "bool", "str", "NoneType"):
                obj_type = "str"
            return f"<{obj_type}>{obj}</{obj_type}>"
        elif isinstance(obj, list):
            return f"<list>{''.join([cls.dumps(i) for i in obj])}</list>"
        elif isinstance(obj, dict):
            result = "".join([f'<key>{key}</key><value>{cls.dumps(value)}</value>' for key, value in obj.items()])
            return f'<dict>{result}</dict>'

    @classmethod
    def loads(cls, string: str):
        return Encoder.decode(cls._loads(string, 0)[0])

    @classmethod
    def _loads(cls, string: str, start):
        if string[start:].startswith("<str>"):
            return cls._get_str(string, start)
        elif string[start:].startswith(("<int>", "<float>")):
            return cls._get_num(string, start)
        elif string[start:].startswith("<bool>"):
            return cls._get_bool(string, start)
        elif string[start:].startswith("<NoneType>"):
            return None, start + len("<NoneType>None</NoneType>")
        elif string[start:].startswith("<list>"):
            return cls._get_list(string, start)
        elif string[start:].startswith("<dict>"):
            return cls._get_dict(string, start)

    @staticmethod
    def _get_str(string, start):
        start += len("<str>")
        end = start + 1
        while string[end:end + len("</str>")] != "</str>":
            end += 1
        return string[start:end], end + len("</str>")

    @staticmethod
    def _get_num(string, start):
        num_type = string[start:].startswith("<int>")
        if num_type:
            start += len("<int>")
        else:
            start += len("<float>")

        end = start + 1
        while len(string) > end and (string[end].isdigit() or string[end] in ('.', '-')):
            end += 1

        num = string[start:end]
        if num_type:
            return int(num), end + len("</int>")
        return float(num), end + len("</float>")

    @staticmethod
    def _get_bool(string, start):
        start += 6
        end = start + 5
        if string[start] == "T":
            end -= 1
        result = string[start:end]
        return result == "True", end + 7

    @classmethod
    def _get_list(cls, string: str, start):
        start += len("<list>") - 1
        end = count_structs(string, start + 1, ('<list>', '</list>'))
        arr = []
        index = start + 1

        while index < end:  # end is start for the next part
            res, index = cls._loads(string, index)
            arr.append(res)

        return arr, end + len("</list>")

    @classmethod
    def _get_dict(cls, string: str, start):
        start += len("<dict>") - 1
        end = count_structs(string, start + 1, ('<dict>', '</dict>'))
        index = start + 1
        result = dict()

        while index < end:
            key, index = cls._get_key(string, index)
            val_str, index = cls._get_value(string, index)
            value = cls._loads(val_str, 0)[0]
            result[key] = value
        return result, end + len("</dict>")

    @staticmethod
    def _get_key(string, start):
        index = start + len("<key>")
        end = index
        while string[end:end + len("</key>")] != "</key>":
            end += 1

        return string[index:end], end + len("</key>")

    @staticmethod
    def _get_value(string, start):
        index = start + len("<value>")
        end = count_structs(string, index, ('<value>', '</value>'))

        return string[index:end], end + len("</value>")
