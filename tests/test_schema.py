import pytest
from deepmerge.exception import InvalidMerge
from jsonschema import ValidationError
from yaml import YAMLError

from dirschema.schema import combine_schemas, load_schemas


@pytest.mark.parametrize(
    "schemas",
    (
        ('{"files": {}, "dirs": {}, "allow_extra_files": false, "allow_extra_dirs": false}',),
        (
            '{"files": {"foo": {"absent": True}}, "dirs": {},'
            '"allow_extra_files": false, "allow_extra_dirs": false}',
        ),
        (
            '{"files": {}, "dirs": {"dir1": {"absent": True}},'
            '"allow_extra_files": false, "allow_extra_dirs": false}',
        ),
    ),
)
def test_load_schemas_good(schemas):
    load_schemas(*schemas)
    # No errors!


@pytest.mark.parametrize(
    "schemas,expected",
    (
        (('{"files": {}, "dirs": {}}',), ValidationError),
        (('{"files": {"foo": {"contains": ["blah"], "absent": true}}}',), ValidationError),
        (('{"dirs": {"foo": {"allow_extra_files": true, "absent": true}}}',), ValidationError),
        (('{"files": {"foo": {"absent": false}}, "dirs": {}}',), ValidationError),
        (("][:badyaml:",), YAMLError),
    ),
)
def test_load_schemas_invalid(schemas, expected):
    try:
        load_schemas(*schemas)
        assert False, "Shouldn't have successfully loaded schema"
    except Exception as e:
        assert isinstance(e, expected)


@pytest.mark.parametrize(
    "schemas,expected",
    (
        (
            ({"files": {"foo": {}}}, {"dirs": {"bar": {}}}),
            {"files": {"foo": {}}, "dirs": {"bar": {}}},
        ),
        (
            ({"files": {"foo": {}, "bar": {}}}, {"files": {"foo": {"contains": ["foo"]}}}),
            {"files": {"foo": {"contains": ["foo"]}, "bar": {}}},
        ),
        (
            ({"files": {"foo": {"contains": ["oof"]}}}, {"files": {"foo": {"contains": ["foo"]}}}),
            {"files": {"foo": {"contains": ["oof", "foo"]}}},
        ),
    ),
)
def test_can_combine(schemas, expected):
    assert combine_schemas(schemas) == expected


@pytest.mark.parametrize(
    "schemas,expected",
    (
        (({"files": {"foo": {}}}, {"files": {"foo": {"absent": True}}}), "foo"),
        (
            (
                {"dirs": {"foo": {"allow_empty_dirs": True}}},
                {"dirs": {"foo": {"allow_empty_dirs": False}}},
            ),
            "allow_empty_dirs",
        ),
    ),
)
def test_cannot_combine(schemas, expected):
    try:
        print(schemas)
        combine_schemas(schemas)
        assert False, "Shouldn't have successfully combined schemas"
    except Exception as e:
        assert isinstance(e, InvalidMerge)
        assert any([expected in a for a in e.args])
