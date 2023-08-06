import regex
from .utility_functions import ObjectConverter
from types import NoneType
from .constants import FIRST_XML_ELEMENT_PATTERN, XML_ELEMENT_PATTERN, KEY_GROUP_NAME, VALUE_GROUP_NAME, XML_SCHEME_SOURCE


class MyXml:
    def dumps(self, obj) -> str:
        obj = ObjectConverter.get_dict(obj)
        return self._dumps(obj, is_first=True)

    def dump(self, obj, source_file):
        source_file.write(self.dumps(obj))

    def load(self, source_file):
        return self.loads(source_file.read())

    def _dumps(self, obj, is_first=False) -> str:
        if type(obj) in (int, float, bool, NoneType):
            return self.__create_xml_element(type(obj).__name__, str(obj), is_first)

        if type(obj) is str:
            data = self.__mask_symbols(obj)
            return self.__create_xml_element(str.__name__, data, is_first)

        if type(obj) is list:
            data = ''.join([self._dumps(o) for o in obj])
            return self.__create_xml_element(list.__name__, data, is_first)

        if type(obj) is dict:
            data = ''.join(
                [f"{self._dumps(item[0])}{self._dumps(item[1])}" for item in obj.items()])
            return self.__create_xml_element(dict.__name__, data, is_first)

        else:
            raise ValueError

    def loads(self, string: str):
        obj = self._loads(string, is_first=True)
        return ObjectConverter.get_object(obj)

    def _loads(self, string: str, is_first=False):
        string = string.strip()
        xml_element_pattern = FIRST_XML_ELEMENT_PATTERN if is_first else XML_ELEMENT_PATTERN

        match = regex.fullmatch(xml_element_pattern, string)

        if not match:
            raise ValueError

        key = match.group(KEY_GROUP_NAME)
        value = match.group(VALUE_GROUP_NAME)

        if key == int.__name__:
            return int(value)

        if key == float.__name__:
            return float(value)

        if key == bool.__name__:
            return value == str(True)

        if key == str.__name__:
            return self.__unmask_symbols(value)

        if key == NoneType.__name__:
            return None

        if key == list.__name__:
            matches = regex.findall(XML_ELEMENT_PATTERN, value)
            return [self._loads(match[0]) for match in matches]

        if key == dict.__name__:
            matches = regex.findall(XML_ELEMENT_PATTERN, value)
            return {self._loads(matches[i][0]):
                    self._loads(matches[i + 1][0]) for i in range(0, len(matches), 2)}
        else:
            raise ValueError

    def __create_xml_element(self, name: str, data: str, is_first=False):
        if is_first:
            return f"<{name} {XML_SCHEME_SOURCE}>{data}</{name}>"
        else:
            return f"<{name}>{data}</{name}>"

    @staticmethod
    def __mask_symbols(string: str) -> str:
        return string.replace('&', "&amp;").replace('<', "&lt;").replace('>', "&gt;"). \
            replace('"', "&quot;").replace("'", "&apos;")

    @staticmethod
    def __unmask_symbols(string: str) -> str:
        return string.replace("&amp;", '&').replace("&lt;", '<').replace("&gt;", '>'). \
            replace("&quot;", '"').replace("&apos;", "'")
