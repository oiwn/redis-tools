"""Test item serializer"""
# pylint: disable=protected-access
# pylint: disable=missing-function-docstring
import json
import bson
import pytest
from rdt.serializers import (
    StrItemSerializer,
    BaseJsonItemSerializer,
    JsonItemSerializer,
    BsonItemSerializer,
)


def test_base_serializer():
    # raise serializer lib if not supported
    with pytest.raises(AssertionError):
        BaseJsonItemSerializer()


def test_str_serializer():
    s = StrItemSerializer()

    assert s.serializer_name == "str"

    assert s.loads("value") == "value"
    assert s.dumps("value") == "value"


def test_json_serializer():
    s = JsonItemSerializer()  # use stdlib json serializer

    # check serializer
    assert s.serializer_name == "json"

    # check functons type
    assert s._loads is json.loads
    assert s._dumps is json.dumps

    # check functions
    assert s.loads('{"a": 1}') == {"a": 1}
    assert s.dumps({"a": 1}) == '{"a": 1}'

    del s


def test_bson_serializer():
    # special cases
    s = BsonItemSerializer()

    # check serializer
    assert s.serializer_name == "bson"

    # check functions type
    assert s._loads.__name__ == bson.BSON.decode.__name__
    assert s._dumps.__name__ == bson.BSON.encode.__name__
