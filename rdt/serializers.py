# pylint: disable=missing-function-docstring,bad-mcs-method-argument
import abc
import importlib
import typing as t


class BaseSerializer(abc.ABCMeta):
    """Base class for serializers"""

    @property
    @abc.abstractmethod
    def serializer_name(self) -> t.Optional[str]:
        raise NotImplementedError

    @abc.abstractmethod
    def loads(self, item: t.Any) -> t.Any:
        raise NotImplementedError

    @abc.abstractmethod
    def dumps(self, item):
        raise NotImplementedError


class StrItemSerializer(metaclass=BaseSerializer):
    """Serialize items to strings"""

    @property
    def serializer_name(self) -> str:
        return "str"

    def loads(self, item):
        return str(item)

    def dumps(self, item):
        return str(item)


class BaseJsonItemSerializer(metaclass=BaseSerializer):
    """Base class implementing common functionality"""

    @property
    def serializer_name(self) -> t.Optional[str]:
        return None

    def __init__(self):
        """Use following serializer for json-like data:"""
        assert self.serializer_name is not None
        _importer = importlib.import_module
        self._loads = _importer(self.serializer_name).loads
        self._dumps = _importer(self.serializer_name).dumps

    def loads(self, item):
        return self._loads(item)

    def dumps(self, item):
        return self._dumps(item)


class JsonItemSerializer(BaseJsonItemSerializer):
    """Serialize items to stdlib json"""

    @property
    def serializer_name(self) -> str:
        return "json"


class UjsonItemSerializer(BaseJsonItemSerializer):
    """Serialize items using ujson library"""

    @property
    def serializer_name(self) -> str:
        return "ujson"


class BsonJsonItemSerializer(BaseJsonItemSerializer):
    """Serialize item using bson.json_util library"""

    @property
    def serializer_name(self) -> str:
        return "bson.json_url"


class BsonItemSerializer(BaseJsonItemSerializer):
    """Serialize item using bson library (binary)"""

    @property
    def serializer_name(self) -> str:
        return "bson"

    def __init__(self):  # pylint: disable=super-init-not-called
        """Use following serializer for json-like data:"""
        assert self.serializer_name is not None
        _importer = importlib.import_module
        self._loads = _importer(self.serializer_name).BSON.decode
        self._dumps = _importer(self.serializer_name).BSON.encode
