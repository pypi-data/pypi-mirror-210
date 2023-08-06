#!/usr/bin/env python3
# coding=utf-8
# SPDX-License-Identifier: MIT
import pytest

import unirange


def test_infinite() -> None:
    assert len(unirange.unirange_to_characters("U+2600..")) == 0x10d200
    assert len(unirange.unirange_to_characters("..U+2600")) == 0x2600 + 1
    assert len(unirange.unirange_to_characters("0x2600..")) == 0x10d200
    assert len(unirange.unirange_to_characters("..0x2600")) == 0x2600 + 1
    assert len(unirange.unirange_to_characters("&#x2600..")) == 0x10d200
    assert len(unirange.unirange_to_characters("..&#x2600")) == 0x2600 + 1
    with pytest.raises(unirange.UnirangeError):
        unirange.unirange_to_characters("..")
        unirange.unirange_to_characters("....")
        unirange.unirange_to_characters("U+2600..U+8000..")


def test_invalids() -> None:
    with pytest.raises(unirange.UnirangeError):
        unirange.unirange_to_characters("U+")
        unirange.unirange_to_characters("U+11FFFF")
        unirange.unirange_to_characters("U+D810")
        unirange.unirange_to_characters("U+DEAD")
        unirange.unirange_to_characters("U+U+U+U+U+")
        unirange.unirange_to_characters("U+..U+2600")
        unirange.unirange_to_characters("6...")
        unirange.unirange_to_characters("A..B..C")
        unirange.unirange_to_characters("00000")
        unirange.unirange_to_characters("00")
        unirange.unirange_to_characters("2600")


def test_surrogates() -> None:
    with pytest.raises(unirange.UnirangeError):
        unirange.unirange_to_characters("U+D800")
        unirange.unirange_to_characters("U+D800..U+DFFF")
        unirange.unirange_to_characters("")
