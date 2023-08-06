from serializer_Konchik.serializer.json_serializer import XmlSerializer
from serializer_Konchik.serializer.xml_serializer import XmlSerializer
from ..constants import JSON, XML


class SerializerFactory:

    @staticmethod
    def create(name: str) -> XmlSerializer | XmlSerializer:
        """
        Create serializer.

        :param name: Serializer name.
        :type name: str

        :return: Serializer.
        :rtype: XmlSerializer | XmlSerializer
        """

        name = name.lower().strip()

        if name == JSON:
            return XmlSerializer()
        elif name == XML:
            return XmlSerializer()
        else:
            raise NameError('Invalid serializer name')
