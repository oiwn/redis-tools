"""Test item serializer"""
# pylint: disable=protected-access
# pylint: disable=missing-function-docstring
import json
import bson
import pytest
from rdt.serializers import ItemSerializer


def test_item_serializer():
    # raise serializer lib if not supported
    with pytest.raises(AssertionError):
        ItemSerializer(serializer="musson")

    s = ItemSerializer()  # use standard json serializer

    # check serializer
    assert s.serializer == "json"

    # check functons type
    assert s._loads is json.loads
    assert s._dumps is json.dumps

    # check functions
    assert s.loads('{"a": 1}') == {"a": 1}
    assert s.dumps({"a": 1}) == '{"a": 1}'

    del s

    # special cases
    s = ItemSerializer(serializer="bson")

    # check serializer
    assert s.serializer == "bson"

    # check functions type
    assert s._loads.__name__ == bson.BSON.decode.__name__
    assert s._dumps.__name__ == bson.BSON.encode.__name__
