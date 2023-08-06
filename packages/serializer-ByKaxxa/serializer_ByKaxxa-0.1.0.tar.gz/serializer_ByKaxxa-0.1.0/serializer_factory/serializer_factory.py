from serializer.serializer import Serializer
from json_serializer.json_serializer import JSON_Serializer
from xml_serializer.xml_serializer import XML_Serializer

class Serializer_Factory:
    """
        This factory for creating serializer {json/xml}
    """
    @staticmethod
    def create_serializer(serializer_frmt: str) -> Serializer:
        """
            Сreate_serialezer will create a serializer depending on its type.

            :param serializer_frmt: type of serializer.
            :type serializer_frmt: str
        """
        serializer_frmt = serializer_frmt.strip().lower()

        if serializer_frmt == "json":
            return JSON_Serializer()
        elif serializer_frmt == "xml":
            return XML_Serializer()
        else:
            raise NameError("From create_serializer: Invalid serializer name [json, xml].")




