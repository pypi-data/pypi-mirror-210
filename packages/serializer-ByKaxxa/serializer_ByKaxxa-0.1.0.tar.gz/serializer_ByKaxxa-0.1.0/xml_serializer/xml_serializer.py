import regex
from serializer.serializer import Serializer
from xml_serializer.constants import KEY, VALUE, ELEMENT_P


class XML_Serializer(Serializer):
    def dumps(self, obj) -> str:
        obj = self.serialize(obj)
        return self.check_value(obj)

    def dump(self, obj, file):
        file.write(self.dumps(obj))

    def loads(self, string):
        obj = self.find_element(string)
        return self.deserialize(obj)

    def load(self, file):
        return self.loads(file.read())

    def find_element(self, string):
        string = string.strip()

        match = regex.fullmatch(ELEMENT_P, string)

        if not match:
            return

        key = match.group(KEY)
        value = match.group(VALUE)

        if key == "int":
            return int(value)

        if key == "float":
            return float(value)

        if key == "str":
            return self.from_special_xml(value)

        if key == "bool":
            return value == "True"

        if key == "complex":
            return complex(value)

        if key == "NoneType":
            return None

        if key == "list":
            matches = regex.findall(ELEMENT_P, value)
            return [self.find_element(match[0]) for match in matches]

        if key == "dict":
            matches = regex.findall(ELEMENT_P, value)
            return {self.find_element(matches[i][0]):
                        self.find_element(matches[i + 1][0]) for i in range(0, len(matches), 2)}

    @staticmethod
    def create_elem(name, value) -> str:
        return f"<{name}>{value}</{name}>"

    def check_value(self, obj) -> str:
        if isinstance(obj, (int, float, bool, complex)):
            return self.create_elem(type(obj).__name__, str(obj))

        if isinstance(obj, str):
            value = self.to_special_xml(obj)
            return self.create_elem("str", value)

        if isinstance(obj, list):
            value = "".join([self.check_value(v) for v in obj])
            return self.create_elem("list", value)

        if isinstance(obj, dict):
            value = "".join([f"{self.check_value(k)}{self.check_value(v)}" for k, v in obj.items()])
            return self.create_elem("dict", value)

        if not obj:
            return self.create_elem("NoneType", "None")

    @staticmethod
    def to_special_xml(string) -> str:
        return string.replace("&", "&amp;").replace("<", "&lt;"). \
            replace(">", "&gt;").replace('"', "&quot;").replace("'", "&apos;")

    @staticmethod
    def from_special_xml(string) -> str:
        return string.replace("&amp;", "&").replace("&lt;", "<"). \
            replace("&gt;", ">").replace("&quot;", '"').replace("&apos;", "'")
