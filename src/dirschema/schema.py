import logging
from pathlib import Path

import jsonschema
import yaml
from deepmerge import STRATEGY_END, Merger
from deepmerge.exception import InvalidMerge

logger = logging.getLogger("dirschema")

SCHEMA_SCHEMA = Path(__file__).parent / "schemas" / "dirschema-v1.yaml"


def fail_if_file_is_absent_and_present(config, path, base, nxt):
    for f in base.get("files", {}).keys():
        if f in nxt.get("files", {}):
            if base["files"][f].get("absent") != nxt["files"][f].get("absent"):
                raise InvalidMerge(
                    f"Cannot merge {base} and {nxt} because {f}"
                    "is specified as both absent and present"
                )

    return STRATEGY_END


def allow_same_simple_values(config, path, base, nxt):
    if base != nxt:
        raise InvalidMerge(f"Cannot merge {path} because values differ ({base}, {nxt})")

    return nxt


schema_merger = Merger(
    [(list, ["append"]), (dict, [fail_if_file_is_absent_and_present, "merge"])],
    [allow_same_simple_values],
    [],
)


def combine_schemas(schemas):
    combined = schemas[0]

    for s in schemas[1:]:
        schema_merger.merge(combined, s)

    return combined


def load_schemas(*schemas):
    loaded = combine_schemas([yaml.safe_load(schema) for schema in schemas])
    schema_schema = yaml.safe_load(open(SCHEMA_SCHEMA).read())
    jsonschema.validate(loaded, schema_schema)
    return loaded
