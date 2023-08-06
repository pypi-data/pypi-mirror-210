"""Diff util for dataclasses."""
from dataclasses import dataclass
from typing import Any

import dictdiffer  # type: ignore

from classdiff.utils import Font, IsDataclass


class DiffType:
    """
    Types of diff.

    DiffType is an enum class for change types that maps to a string
    representation of how to represent each diff type.
    """

    ADDED = "+"
    REMOVED = "-"
    CHANGED = "~"
    UNCHANGED = " "


@dataclass
class DiffInfo:
    """
    Diff context needed to present the diff.

    Information about a diff on a dataclass. The class contains information
    needed to do proper TTY representation of a human readable diff on a
    dataclass.
    """

    indent: int
    diff_type: str
    key: str | None
    value: Any
    previous_value: Any | None

    def __repr__(self):
        """
        Pretty printable diff.

        Printing the `DiffInfo` class will print it with correct colors and
        values.
        """
        # Start and end of a class does not contain a key so just set the key to
        # an empty string if the diff value is None.
        key = f"{self.key} = "
        if self.key is None:
            key = ""

        # If we have a previous value ensure to represent the old and new value
        # so it's easy to interpret the change.
        value = self.value
        if self.previous_value is not None:
            value = (
                f"{Font.RED}{self.previous_value}{Font.ENDC} => "
                f"{Font.GREEN}{self.value}{Font.ENDC}"
            )

        match self.diff_type:
            case DiffType.CHANGED:
                color = Font.YELLOW
            case DiffType.ADDED:
                color = Font.GREEN
            case DiffType.REMOVED:
                color = Font.RED
            case _:
                color = Font.ENDC

        indent = " " * (2 * self.indent)

        return f"{color}{self.diff_type} {indent}{key}{value}{Font.ENDC}"


def diff(  # noqa: PLR0915
    a: IsDataclass | object | None,
    b: IsDataclass | object | None,
    indent=1,
    class_key=None,
) -> list[DiffInfo]:
    """
    Diff two dataclasses.

    Calculate the diff between two passed (data)classes or dictionaries.

    Arguments:
        a: The first dataclass
        b: The second dataclass
        indent: The current level in the dataclass
        class_key: The key in a parent dict where the class was found

    Returns:
        A list of `DiffInfo`
    """
    if a is None and b is None:
        return []

    if isinstance(a, dict):
        a_dict = a
    elif a is None:
        a_dict = {}
    else:
        a_dict = a.__dict__

    if isinstance(b, dict):
        b_dict = b
    elif b is None:
        b_dict = {}
    else:
        b_dict = b.__dict__

    changeset = {}
    if a is not None and b is not None:
        if type(a) != type(b):
            return diff(a, None, indent, class_key) + diff(None, b, indent, class_key)

        d = dictdiffer.diff(a_dict, b_dict)

        for diff_type, key, diff_values in d:
            # TODO: We currently only handles `change` types but we want to
            # support `add` and `remove` as well, at least for lists.
            if diff_type != "change":
                continue

            if isinstance(key, list):
                # TODO: Currently we only show the old and new values as is in
                # the full list, might want to use `dictdiff` output to
                # highlight what indexes are changed.
                key = key[0]  # noqa: ruff PLW2901
                changeset[key] = (a_dict[key], b_dict[key])
            else:
                changeset[key] = diff_values

    if a is not None:
        class_name = a.__class__.__name__
        primary_data = a_dict
        secondary_data = b_dict
        keys = a_dict.keys()
        secondary_keys = b_dict.keys()
    else:
        class_name = b.__class__.__name__
        primary_data = b_dict
        secondary_data = a_dict
        keys = b_dict.keys()
        secondary_keys = a_dict.keys()

    keys_missing = list(filter(lambda x: x not in keys, secondary_keys))
    all_keys = sorted(
        [(x, "modified") for x in keys] + [(x, "deleted") for x in keys_missing]
    )

    # We don't want to print dictionaries as
    #  dict(
    #    key=value
    #  )
    # So if the class is a dict, set name to just "{" and close the class with
    # "}".
    class_opening = "("
    class_termination = ")"
    if class_name == "dict":
        class_name = ""
        class_opening = "{"
        class_termination = "}"

    if b is None:
        diff_type = DiffType.ADDED
    elif a is None:
        diff_type = DiffType.REMOVED
    else:
        diff_type = DiffType.UNCHANGED

    class_diff = [
        DiffInfo(
            indent=indent - 1,
            diff_type=diff_type if len(changeset) == 0 else DiffType.CHANGED,
            key=class_key,
            value=f"{Font.BOLD}{Font.UNDERLINE}{class_name}{Font.NO_UNDERLINE}{Font.NO_BOLD}{class_opening}",
            previous_value=None,
        )
    ]

    for key, change_type in all_keys:
        if change_type == "deleted":
            class_diff.extend(diff(None, secondary_data[key], indent + 1, key))
            continue

        value = primary_data[key]

        if hasattr(value, "__dict__"):
            value = value.__dict__

        if key in changeset and not isinstance(value, dict):
            class_diff.append(
                DiffInfo(
                    indent=indent,
                    diff_type=DiffType.CHANGED,
                    key=key,
                    value=value,
                    previous_value=changeset[key][1],
                )
            )
            continue

        if isinstance(value, dict):
            inner_a, inner_b = None, None
            if a is not None:
                inner_a = getattr(a, key) if hasattr(a, key) else a_dict.get(key)

            if b is not None:
                inner_b = getattr(b, key) if hasattr(b, key) else b_dict.get(key)

            class_diff.extend(diff(inner_a, inner_b, indent + 1, key))
            continue

        class_diff.append(
            DiffInfo(
                indent=indent,
                diff_type=diff_type,
                key=key,
                value=value,
                previous_value=None,
            )
        )

    class_diff.append(
        DiffInfo(
            indent=indent - 1,
            diff_type=diff_type if len(changeset) == 0 else DiffType.CHANGED,
            key=None,
            value=class_termination,
            previous_value=None,
        )
    )

    return class_diff
