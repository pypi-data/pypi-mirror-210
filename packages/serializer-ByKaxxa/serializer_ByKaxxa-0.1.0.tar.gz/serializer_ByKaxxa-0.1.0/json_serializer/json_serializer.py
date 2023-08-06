import regex
from serializer.serializer import Serializer
from json_serializer.constants import JSON_INT, JSON_STR, JSON_BOOL, JSON_NONE, JSON_FLOAT, \
    JSON_VALUE, JSON_COMPLEX, JSON_DICT_RECURSION, JSON_LIST_RECURSION


class JSON_Serializer(Serializer):
    def dumps(self, obj) -> str:
        obj = self.serialize(obj)
        return self.beautiful_string(obj)

    def dump(self, obj, file):
        file.write(self.dumps(obj))

    def loads(self, string):
        obj = self.find_element(string)
        return self.deserialize(obj)

    def load(self, file):
        return self.loads(file.read())

    def find_element(self, string):
        string = string.strip()

        match = regex.fullmatch(JSON_INT, string)
        if match:
            return int(match.group(0))

        match = regex.fullmatch(JSON_STR, string)
        if match:
            res = match.group(0)
            res = res.replace("\\\\", "\\"). \
                replace(r"\"", '"'). \
                replace(r"\'", "'")
            return res[1:-1]

        match = regex.fullmatch(JSON_FLOAT, string)
        if match:
            return float(match.group(0))

        match = regex.fullmatch(JSON_BOOL, string)
        if match:
            return match.group(0) == "True"

        match = regex.fullmatch(JSON_NONE, string)
        if match:
            return None

        if string.startswith("[") and string.endswith("]"):
            string = string[1:-1]
            matches = regex.findall(JSON_VALUE, string)
            return [self.find_element(match[0]) for match in matches]

        if string.startswith("{") and string.endswith("}"):
            string = string[1:-1]
            matches = regex.findall(JSON_VALUE, string)
            return {self.find_element(matches[i][0]):
                    self.find_element(matches[i + 1][0])
                    for i in range(0, len(matches), 2)}

    def beautiful_string(self, value) -> str:
        if isinstance(value, str):
            return '"' + \
                value.replace("\\", "\\\\"). \
                    replace('"', "\""). \
                    replace("'", "\'") + '"'

        elif isinstance(value, (int, float, complex)):
            return str(value)

        elif isinstance(value, bool):
            return "true" if value else "false"

        elif isinstance(value, list):
            return "[" + ", ".join([self.beautiful_string(val) for val in value]) + "]"

        if isinstance(value, dict):
            return "{" + ", ".join(
                [f"{self.beautiful_string(k)}: {self.beautiful_string(v)}" for k, v in value.items()]) + "}"