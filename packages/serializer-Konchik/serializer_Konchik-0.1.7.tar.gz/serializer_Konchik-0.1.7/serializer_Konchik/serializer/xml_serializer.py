import regex
import builtins
from typing import Any
from serializer_Konchik.packer import Packer, Unpacker
from serializer_Konchik.serializer.base_serializer import BaseSerializer
from types import NoneType
from ..constants import (PRIMITIVES, KEY, VALUE,
                         XmlRegularExpression as Expression)


class XmlSerializer(BaseSerializer):

    def dumps(self, obj: Any) -> str:
        """
        Convert an object to string of 'XML' format.

        :param obj: Any python object.
        :type obj: Any

        :return: String of 'XML' format.
        :rtype: str
        """

        packed: dict = Packer.pack(obj)
        return self._convert(packed)

    def loads(self, string: str):
        """
        Convert string of 'XML' format to object.

        :param string: String of 'XML' format.
        :type string: str

        :return: Python object.
        :rtype: Any
        """

        packed: dict = self._deconvert(string)
        return Unpacker.unpack(packed)

    def _convert(self, obj: dict) -> str:
        """
        Convert dictionary that represents object
        to a string of 'XML' format

        :param obj: Dictionary that represents object.
        :type obj: dict

        :return: String of 'XML' format.
        :rtype: str
        """

        if isinstance(obj, PRIMITIVES):
            if isinstance(obj, str):
                return XmlSerializer.create_xml_item(type(obj).__name__, XmlSerializer.to_special_xml(obj))
            else:
                return XmlSerializer.create_xml_item(type(obj).__name__, str(obj))

        if isinstance(obj, list):
            return XmlSerializer.create_xml_item(type(obj).__name__, "".join([self._convert(item) for item in obj]))

        if isinstance(obj, dict):
            return XmlSerializer.create_xml_item(type(obj).__name__, "".join(
                [f"{self._convert(key)}{self._convert(value)}" for key, value in obj.items()]))

    def _deconvert(self, string: str) -> dict:
        """
        Convert string of 'XML' format to
        dictionary that represents object.

        :param string: String of 'XML' format.
        :type string: str

        :return: Dictionary that represents object.
        :rtype: dict
        """

        string = string.strip()

        match = regex.fullmatch(Expression.ITEM.value, string)
        if not match:
            return

        key = match.group(KEY)
        value = match.group(VALUE)

        if key in map(lambda p: p.__name__, PRIMITIVES):
            if key == str.__name__:
                return XmlSerializer.from_special_xml(value)
            elif key == NoneType.__name__:
                return None
            elif key == bool.__name__:
                return True if value == 'True' else False
            else:
                return getattr(builtins, key)(value)

        if key == list.__name__:
            matches = regex.findall(Expression.ITEM.value, value)
            return [self._deconvert(match[0]) for match in matches]

        if key == dict.__name__:
            matches = regex.findall(Expression.ITEM.value, value)
            return {self._deconvert(matches[i][0]): self._deconvert(matches[i + 1][0])
                    for i in range(0, len(matches), 2)}

    @staticmethod
    def create_xml_item(tag_name, value):
        return f"<{tag_name}>{value}</{tag_name}>"

    @staticmethod
    def to_special_xml(string):
        return string.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"). \
            replace('"', "&quot;").replace("'", "&apos;")

    @staticmethod
    def from_special_xml(string):
        return string.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">"). \
            replace("&quot;", '"').replace("&apos;", "'")
