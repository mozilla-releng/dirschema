from pathlib import Path

import jsonschema
import yaml

SCHEMA_SCHEMA = Path(__file__).parent / "schemas" / "dirschema-v1.yaml"


def load_schema(schema):
    loaded = yaml.safe_load(schema)
    schema_schema = yaml.safe_load(open(SCHEMA_SCHEMA).read())
    jsonschema.validate(loaded, schema_schema)
    return loaded
