import pytest
from jsonschema import ValidationError

from dirschema.schema import load_schema


def test_load_schema_good():
    good_schema = '{"files": {}, "dirs": {}, "allow_extra_files": false, "allow_extra_dirs": false}'
    expected = {"files": {}, "dirs": {}, "allow_extra_files": False, "allow_extra_dirs": False}
    loaded = load_schema(good_schema)
    assert loaded == expected


@pytest.mark.parametrize(
    "schema,expected", (('{"files": {}, "dirs": {}}', ValidationError), ("{badjson}", ValueError))
)
def test_load_schema_invalid(schema, expected):
    try:
        load_schema(schema)
        assert False, "Shouldn't have successfully loaded schema"
    except Exception as e:
        assert isinstance(e, expected)
