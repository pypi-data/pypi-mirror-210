"""Diff two datacalsses as JSON."""
import dataclasses
import difflib
import json

from . import IsDataclass


class DCJSONEncoder(json.JSONEncoder):
    """Encoder for dataclasses."""

    def default(self, o):
        """The default implementation for JSONEncoder."""
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)

        return super().default(o)


def diff_json(a: IsDataclass, b: IsDataclass) -> list[str]:
    """Diff dataclasses as JSON.

    Will convert the dataclasses to JSON and return the unixdiff of the JSON
    representaton.

    Arguments:
        a: The first dataclass
        b: The second dataclass

    Returns:
        A list of unixdiff lines
    """
    a_json = json.dumps(a, indent=2, sort_keys=True, cls=DCJSONEncoder).splitlines(
        keepends=True
    )

    b_json = json.dumps(b, indent=2, sort_keys=True, cls=DCJSONEncoder).splitlines(
        keepends=True
    )

    return list(difflib.Differ().compare(a_json, b_json))
