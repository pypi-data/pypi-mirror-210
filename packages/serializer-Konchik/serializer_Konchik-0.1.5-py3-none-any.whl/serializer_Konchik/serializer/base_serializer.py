from abc import ABC, abstractmethod
from typing import Any, IO


class BaseSerializer(ABC):

    @abstractmethod
    def dumps(self, obj: Any) -> str:
        """
        Convert an object to string of certain format.

        :param obj: Any python object.
        :type obj: Any

        :return: String of certain format.
        :rtype: str
        """

        return NotImplementedError('"dumps" method not implemented')

    def dump(self, obj: Any, file: IO) -> None:
        """
        Write an object to file of certain format.

        :param obj: Any python object.
        :type obj: Any

        :param file: File object.
        :type file: IO
        """

        file.write(self.dumps(obj))

    @abstractmethod
    def loads(self, string: str):
        """
        Convert string of certain format to object.

        :param string: String of certain format.
        :type string: str

        :return: Python object.
        :rtype: Any
        """

        return NotImplementedError('"loads" method not implemented')

    def load(self, file: IO):
        """
        Read file of certain format and convert in to object.

        :param file: File object.
        :type file: IO

        :return: Python object.
        :rtype: Any
        """

        return self.loads(file.read())
