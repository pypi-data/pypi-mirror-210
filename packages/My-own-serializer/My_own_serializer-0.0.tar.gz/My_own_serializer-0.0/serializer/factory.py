from .constants import Serializer
from .myjson import MyJson
from .myxml import MyXml


class Factory:

    @staticmethod
    def create_serializer(serializer: Serializer):
        if Serializer.Json:
            return MyJson()

        elif Serializer.Xml:
            return MyXml()
