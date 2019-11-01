import json
from pathlib import Path

import jsonschema

SCHEMA_SCHEMA = Path(__file__).parent / "schemas" / "dirschema-v1.json"


def load_schema(schema):
    loaded = json.loads(schema)
    schema_schema = json.load(open(SCHEMA_SCHEMA))
    jsonschema.validate(loaded, schema_schema)
    return loaded
