from .json_serializer import JsonSerializer
from .xml_serializer import XmlSerializer


class Serializer:
    @staticmethod
    def create_serializer(answer):
        if answer == "json":
            return JsonSerializer()
        elif answer == "xml":
            return XmlSerializer()
        else:
            raise ValueError("Incorrect input of serializer's type")
