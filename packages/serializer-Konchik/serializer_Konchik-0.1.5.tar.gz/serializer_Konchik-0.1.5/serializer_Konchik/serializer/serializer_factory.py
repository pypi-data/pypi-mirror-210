from serializer_Konchik.serializer.json_serializer import JsonSerializer
from serializer_Konchik.serializer.xml_serializer import XmlSerializer
from ..constants import JSON, XML


class SerializerFactory:

    @staticmethod
    def create(name: str) -> JsonSerializer | XmlSerializer:
        """
        Create serializer.

        :param name: Serializer name.
        :type name: str

        :return: Serializer.
        :rtype: JsonSerializer | XmlSerializer
        """

        name = name.lower().strip()

        if name == JSON:
            return JsonSerializer()
        elif name == XML:
            return XmlSerializer()
        else:
            raise NameError('Invalid serializer name')
