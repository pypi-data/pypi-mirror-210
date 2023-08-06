#!/usr/bin/env python3
# coding=utf-8
# SPDX-License-Identifier: MIT
r"""
Unirange is a notation for specifying multiple Unicode codepoints.

A unirange comprises comma-delimited **components**.

A **part** is a notation for a single character, like ``A``, ``U+2600``, or ``0x7535``.
It is matched by the regular expression ``!?(?:0x|U\+|&#x)([0-9A-F]{1,7});?|(.)``

A **range** is two **parts** split by ``..`` (two dots) or ``-`` (a hyphen).
It is matched by the regular expression ``(?PART(?:-|\.\.)PART)``

A **component** comprises either a **range** or a **part**.
It is matched by the regular expression ``(RANGE|PART)``

The full unirange notation is matched by the regular expression ``(?:COMPONENT, ?)*``

Exclusion can be applied to any component by prefixing it with a ``!``.
This will instead perform the *difference* (subtraction) on the current set of characters.

----

Component
---------

A component is either a *range*, or a *part*.
These components define what characters are included or excluded by the unirange.

Part
----

A part is a *single* character notation.
In a *range*, there exist two parts, split by ``..`` or ``-``.
In the range ``U+2600..U+26FF``, ``U+2600`` and ``U+26FF`` are parts.

Parts can match any of these regular expressions:

* ``U\+.{1,6}``
* ``&#x.{1,6}``
* ``0x.{1,6}``
* ``.``

.. warning::
    If more than one character is in a part, and it is *not* prefixed, it is **invalid**.
    For example, ``2600`` is not a valid part, but ``U+2600`` is.

.. note::
    There is no way to specify a codepoint in a base system other than **hexadecimal**.
    ``&#1234`` is not valid.

Range
-----

A range is two *parts* separated by ``..`` or ``-``.

Implied infinite expansion
~~~~~~~~~~~~~~~~~~~~~~~~~~

If either (but not both) part of the range is absent, it is called **implied infinite expansion** (IIE).
With IIE, the range's boundaries are implied to become to lower or upper limits of the Unicode character set.

If the first part is absent, the first part becomes U+0000.
If the second part is absent, it becomes U+10FFFF.

This means that the range ``U+2600..`` will result in characters from U+2600 to U+10FFFF.
It is semantically equivalent to ``U+2600..U+10FFFF``.

This also applies to the reverse: the range ``..U+2600`` will result in characters from U+0000 to U+2600.
Likewise, it is equivalent to ``U+0000..U+2600``.

Exclusion
---------

To exclude a character from being included in a resulting range, prefix a component with a ``!``.
This will prevent it from being included in the range, regardless of what other parts indicate.

For example, ``U+2600..U+26FF, U+2704, !U+2605`` will include the codepoints from U+2600 **up to** U+2605,
and then from U+2606 to U+26FF, as well as U+2704.

You can exclude ranges as well. Either part of a range may be prefixed with a ``!`` to label that part as an
exclusion. ``!U+2600..U+267F``, ``!U+2600..!U+267F``, and ``!U+2600..!U+267F`` result in the same range:
no codepoints from U+2600 to U+267F.

**Exclusions must come after the inclusions, or else they will be overridden.**

.. important::
    | The order of your components matters when excluding.
    | Components after an exclusion that conflict with it *will* obsolete it, overriding it.
    | For example, ``!U+2600..U+2650,U+2600..U+26FF`` will result in the effective range of ``U+2600-26FF``.

----

Unirange is licensed under the `MIT license <https://mit-license.org/>`_.

"""
from __future__ import annotations

import re
import sys

__author__ = "WhoAteMyButter"
__version__ = (0, 6)
__license__ = "MIT"

if sys.version_info < (3, 11, 0):
    raise RuntimeError(
        f"minimum Python version is 3.11.0, you are running {sys.version.split(' ', 1)[0]}"
    )


class UnirangeError(Exception):
    """Generic unirange error."""


UNIRANGE_PART = re.compile(r"!?(?:0x|U\+|&#x)([0-9A-F]{1,7});?|(.)", re.I)
UNIRANGE_RANGE_DELIMITER = re.compile(r"-|\.\.")
UNIRANGE_RANGE = re.compile(
    f"({UNIRANGE_PART.pattern}?)({UNIRANGE_RANGE_DELIMITER.pattern})({UNIRANGE_PART.pattern}?)",
    re.I,
)
UNIRANGE_COMPONENT = re.compile(
    f"({UNIRANGE_RANGE.pattern}|{UNIRANGE_PART.pattern})", re.I
)
UNIRANGE_COMPONENT_DELIMITER = re.compile(", ?")
UNIRANGE_FULL = re.compile(
    f"(({UNIRANGE_COMPONENT.pattern}{UNIRANGE_COMPONENT_DELIMITER.pattern})*)", re.I
)


def part_to_character(unirange_part: str) -> str:
    """
    Given a part of a unirange, return the character it translates to.

    This notation should match this regular expression :const:`UNIRANGE_PART`.

    >>> part_to_character("U+2600")
    '☀'
    >>> part_to_character("0x2541")
    '╁'

    :param unirange_part: A unirange part.
    :returns: A single character.
    :raises UnirangeError: If a surrogate (U+D800..U+DFFF) is in the part.
    """
    if parts := UNIRANGE_PART.fullmatch(unirange_part):
        if (single_char := parts.group(2)) is not None:
            return single_char
        if (codepoint := int(parts.group(1), 16)) in range(0xD800, 0xDFFF + 1):
            raise UnirangeError(f'Surrogates are not allowed, got "U+{codepoint:04X}"')
        if codepoint > 0x10FFFF:
            raise UnirangeError(f'Invalid Unicode codepoints are not allowed, got "U+{codepoint:04X}"')
        return chr(codepoint)
    raise UnirangeError(f'Invalid unirange part: "{unirange_part}"')


def component_update(unirange_component: str, update: set[str]) -> None:
    """
    Update `update` with the characters described in `unirange_component`.

    This notation should match this regular expression :const:`UNIRANGE_RANGE`.

    >>> s = {"\u2600", "\u2601"}
    >>> component_update("!U+2600", s)
    >>> s
    {'☁'}

    :param unirange_component:
        A unirange component.
    :param update:
        A set of the already-included characters.
        This is required for applying exclusion.
    :raises UnirangeError: If the component is invalid.
    """
    split = UNIRANGE_RANGE_DELIMITER.split(unirange_component, 1)
    len_split = len(split)
    if len_split == 2 and not (split[0] == "" and split[1] == ""):
        if not split[0]:
            # ..U+XXXX
            split[0] = "U+0"
        elif not split[1]:
            # U+XXXX..
            split[1] = "U+10FFFF"
        ranges = set(
            chr(i)
            for i in range(
                ord(part_to_character(split[0])),
                # + 1 to be inclusive of last codepoint
                ord(part_to_character(split[1])) + 1,
            )
            if i not in range(0xD800, 0xDFFF + 1)
        )
        if split[0].startswith("!") or split[1].startswith("!"):
            # This is an exclusion, remove it
            update.difference_update(ranges)
        else:
            update.update(ranges)
    elif len_split == 1:
        part = part_to_character(split[0])

        if split[0].startswith("!"):
            # This is an exclusion, remove it
            update.difference_update(part)
        else:
            update.update(part)
    else:
        raise UnirangeError(f'Invalid unirange component: "{unirange_component}"')


def unirange_to_characters(unirange: str) -> set[str]:
    r"""
    Return a set of characters that corresponds to `unirange`.

    >>> unirange_to_characters("U+2600..U+260f, A")
    {'☎', '☌', '☉', '☂', '☃', '☆', '★', '☄', '☋', '☍', '☁', '☏', '☀', '☇', '☈', 'A', '☊'}

    :param unirange: A unirange string.
    :returns: A set of characters.
    :raises UnirangeError: If the unirange is invalid.
    """
    current_coverage: set[str] = set()
    for component in UNIRANGE_COMPONENT_DELIMITER.split(unirange):
        if UNIRANGE_RANGE.fullmatch(component):
            # It's a range.
            component_update(component, current_coverage)
        elif UNIRANGE_PART.fullmatch(component):
            # It's a part.
            if component.startswith("!"):
                # This is an exclusion, remove it.
                current_coverage.difference_update(part_to_character(component))
            else:
                current_coverage.update(part_to_character(component))
        else:
            # It's neither, ???
            raise UnirangeError(f"Invalid unirange notation: {component}")
    return current_coverage


def is_character_in_unirange(character: str, unirange: str) -> bool:
    """
    Return if `character` would be present in `unirange`.

    >>> is_character_in_unirange("\u2600", "U+2540..U+2605")
    True
    >>> is_character_in_unirange("\u2600", "A")
    False

    :param character: A single character string.
    :param unirange: A unirange string.
    :returns: If `character` will be present in `unirange`.
    """
    return character in unirange_to_characters(unirange)
