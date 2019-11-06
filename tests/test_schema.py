import pytest
from jsonschema import ValidationError
from yaml import YAMLError

from dirschema.schema import load_schema


@pytest.mark.parametrize(
    "schema",
    (
        '{"files": {}, "dirs": {}, "allow_extra_files": false, "allow_extra_dirs": false}',
        '{"files": {"foo": {"absent": True}}, "dirs": {},'
        '"allow_extra_files": false, "allow_extra_dirs": false}',
        '{"files": {}, "dirs": {"dir1": {"absent": True}},'
        '"allow_extra_files": false, "allow_extra_dirs": false}',
    ),
)
def test_load_schema_good(schema):
    load_schema(schema)
    # No errors!


@pytest.mark.parametrize(
    "schema,expected",
    (
        ('{"files": {}, "dirs": {}}', ValidationError),
        ('{"files": {"foo": {"contains": ["blah"], "absent": true}}}', ValidationError),
        ('{"dirs": {"foo": {"allow_extra_files": true, "absent": true}}}', ValidationError),
        ('{"files": {"foo": {"absent": false}}, "dirs": {}}', ValidationError),
        ("][:badyaml:", YAMLError),
    ),
)
def test_load_schema_invalid(schema, expected):
    try:
        load_schema(schema)
        assert False, "Shouldn't have successfully loaded schema"
    except Exception as e:
        assert isinstance(e, expected)
