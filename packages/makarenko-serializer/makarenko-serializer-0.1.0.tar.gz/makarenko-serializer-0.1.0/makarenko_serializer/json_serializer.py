from .encoder import Encoder
from .help_funcs import count_braces


class JsonSerializer:

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
        if isinstance(obj, bool):
            return str(obj).lower()
        elif isinstance(obj, int | float):
            return str(obj)
        elif isinstance(obj, str):
            return f'"{obj}"'
        elif isinstance(obj, list):
            return f"[{', '.join([cls.dumps(i) for i in obj])}]"
        elif isinstance(obj, dict):
            result = ", ".join([f'"{key}": {cls.dumps(value)}' for key, value in obj.items()])
            return f'{{{result}}}'
        else:
            return "null"

    @classmethod
    def loads(cls, string: str):
        return Encoder.decode(cls._loads(string, 0)[0])

    @classmethod
    def _loads(cls, string: str, start):
        if string[start] == '"':
            return cls._get_str(string, start)
        elif string[start].isdigit() or string[start] == '-':
            return cls._get_num(string, start)
        elif string[start] == "t" or string[start] == "f":
            return cls._get_bool(string, start)
        elif string[start] == "n":
            return None, start + 4
        elif string[start] == '[':  # for list
            return cls._get_list(string, start)
        elif string[0] == '{':  # for dict
            return cls._get_dict(string, start)
        else:
            return string

    @staticmethod
    def _get_str(string, start):
        end = start + 1
        while string[end] != '"':
            end += 1
        return string[start + 1: end], end + 1

    @staticmethod
    def _get_num(string, start):
        end = start + 1
        while len(string) > end and (string[end].isdigit() or string[end] == "."):
            end += 1

        num = string[start:end]
        if num.count("."):
            return float(num), end
        return int(num), end

    @staticmethod
    def _get_bool(string, start):
        result = string[start] == "t"
        num_of_letters = 5
        if result:
            num_of_letters = 4
        return result, start + num_of_letters

    @classmethod
    def _get_list(cls, string: str, start):
        end = count_braces(string, start + 1, ('[', ']'))
        arr = []
        index = start + 1

        while index < end - 2:  # end is start for the next part
            while string[index].startswith((' ', ',', '\n')):
                index += 1
            res, index = cls._loads(string, index)
            arr.append(res)

        return arr, end

    @classmethod
    def _get_dict(cls, string: str, start):
        end = count_braces(string, start + 1, ('{', '}'))
        index = start + 1
        result = dict()

        while index < end - 2:
            while string[index].startswith((' ', ',', '\n')):
                index += 1
            key, index = cls._get_str(string, index)

            while string[index].startswith((' ', ',', '\n', ':')):
                index += 1
            value, index = cls._loads(string, index)
            result[key] = value
        return result, end
