import inspect


def get_class(func):
    clas = getattr(inspect.getmodule(func),
                   func.__qualname__.split(".<locals>", 1)[0].rsplit(".", 1)[0])
    if isinstance(clas, type):
        return clas


def is_iterable(obj):
    return (
            hasattr(obj, "__iter__")
            and hasattr(obj, "__next__")
            and callable(obj.__iter__)
            and obj.__iter__() is obj
    )


def count_braces(string, index, braces_type):
    braces_count = 1
    while braces_count:
        if string[index] == braces_type[0]:
            braces_count += 1
        if string[index] == braces_type[1]:
            braces_count -= 1
        index += 1

    if index == len(string):
        index += 1
    return index


def count_structs(string, index, braces_type):
    braces_count = 1
    while braces_count:
        if string[index:index + len(braces_type[0])] == braces_type[0]:
            braces_count += 1
        if string[index:index + len(braces_type[1])] == braces_type[1]:
            braces_count -= 1
        index += 1
    return index - 1
