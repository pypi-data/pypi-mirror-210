import pytest, json
from jschemator import Schema
from jschemator.fields import StringField


class Item(Schema):
    name = StringField()


def test_creation():
    e = Item(name="foo")
    assert e.name == "foo"


def test_incorrect_creation():
    with pytest.raises(ValueError):
        Item(name=2)


def test_from_dict():
    e = Item(**{"name": "foo"})
    assert e.name == "foo"


def test_to_dict():
    a = Item(**{"name": "foo"})
    assert a.to_dict() == {"name": "foo"}

    b = Item(**{"name": "baz"})
    assert b.to_dict() == {"name": "baz"}


def test_json_schema():
    e = Item(**{"name": "foo"})
    assert e.json_schema() == {
        "type": "object",
        "properties": {"name": {"type": "string"}},
    }


def test_repr():
    e = Item(**{"name": "foo"})
    assert str(e) == "{'name': 'foo'}"


def test_json_array_of_items():
    arr = [Item(name="foo"), Item(name="bar")]
    json.dumps(Item(name="foo"))
    json.dumps(arr)
    assert json.loads(json.dumps(arr)) == arr
