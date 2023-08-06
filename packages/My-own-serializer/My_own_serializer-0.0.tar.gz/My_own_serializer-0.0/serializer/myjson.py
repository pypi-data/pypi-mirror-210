from .utility_functions import ObjectConverter
from types import NoneType, ModuleType, CodeType, FunctionType, CellType
import re
import regex
from .constants import NULL_LITERAL, INT_PATTERN, FLOAT_PATTERN, BOOL_PATTERN,\
    TRUE_LITERAL, STRING_PATTERN, NULL_PATTERN, VALUE_PATTERN


class MyJson:
    def dumps(self, obj) -> str:
        obj = ObjectConverter.get_dict(obj)

        return self._dumps(obj)

    def dump(self, obj, source_file):
        source_file.write(self.dumps(obj))

    def load(self, source_file):
        return self.loads(source_file.read())

    def _dumps(self, obj) -> str:
        if type(obj) in (int, float):
            return str(obj)

        if type(obj) is bool:
            return str(obj).lower()

        if type(obj) is str:
            return '"' + self.__mask_quotes(obj) + '"'

        if type(obj) is NoneType:
            return NULL_LITERAL

        if type(obj) is list:
            return '[' + ", ".join([self._dumps(item) for item in obj]) + ']'

        if type(obj) is dict:
            return '{' + ", ".join([f"{self._dumps(item[0])}: "
                                    f"{self._dumps(item[1])}" for item in obj.items()]) + '}'
        else:
            raise ValueError

    def loads(self, string: str):
        obj = self._loads(string)
        return ObjectConverter.get_object(obj)

    def _loads(self, string: str):
        string = string.strip()

        match = re.fullmatch(INT_PATTERN, string)
        if match:
            return int(match.group(0))

        match = re.fullmatch(FLOAT_PATTERN, string)
        if match:
            return float(match.group(0))

        match = re.fullmatch(BOOL_PATTERN, string)
        if match:
            return match.group(0) == TRUE_LITERAL

        match = re.fullmatch(STRING_PATTERN, string)
        if match:
            ans = match.group(0)
            ans = self.__unmask_quotes(ans)
            return ans[1:-1]

        match = re.fullmatch(NULL_PATTERN, string)
        if match:
            return None

        # List
        if string[0] == '[' and string[-1] == ']':
            string = string[1:-1]
            matches = regex.findall(VALUE_PATTERN, string)
            return [self._loads(match[0]) for match in matches]

        # Dict
        if string[0] == '{' and string[-1] == '}':
            string = string[1:-1]
            matches = regex.findall(VALUE_PATTERN, string)

            return {self._loads(matches[i][0]):
                    self._loads(matches[i + 1][0]) for i in range(0, len(matches), 2)}

        else:
            raise ValueError

    @staticmethod
    def __mask_quotes(string: str) -> str:
        return string.replace('\\', "\\\\").replace('"', r"\"").replace("'", r"\'")

    @staticmethod
    def __unmask_quotes(string: str) -> str:
        return string.replace('\\\\', "\\").replace(r"\"", '"').replace(r"\'", "'")
