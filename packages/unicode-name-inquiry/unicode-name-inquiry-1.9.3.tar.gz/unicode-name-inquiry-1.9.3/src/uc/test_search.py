# SPDX-License-Identifier: MIT
"""Test uc.search."""

import sys

from collections.abc import Generator

import pytest

from uc.search import search_name

# NB. Some of these tests could fail in the future if Unicode adds
# new characters with unfortunately conflicting names.

def chars(lo: int = 0,
          hi: int = sys.maxunicode + 1) -> Generator[str, None, None]:
    return (chr(i) for i in range(lo, hi))

def test_search_name_exact():
    r = search_name('exact', ['8', 'Digit nine', '\uABCD', 'fail'],
                    chars(0, 0x7F))
    assert set(r) == set('89')

def test_search_name_match():
    r = search_name('match', ['it ni', 'dig'], chars(0, 0x7F))
    s = search_name('match', ['it ni', 'dig'], chars(0, 0x7F), any)
    assert set(r) == set('9')
    assert set(s) == set('0123456789')

def test_search_name_word():
    r = search_name('word', ['nine', 'digit'], chars(0, 0x7F))
    s = search_name('word', ['nine', 'digit'], chars(0, 0x7F), any)
    assert set(r) == set('9')
    assert set(s) == set('0123456789')

def test_search_name_egrep():
    r = search_name('egrep', ['c[eio][lmn]'], chars(0, 0x7F))
    assert set(r) == set('%,:;@^`')

def test_search_name_glob():
    r = search_name('glob', ['c[eo]*n'], chars(0, 0x7F))
    assert set(r) == set('%:;')

def test_search_name_html():
    r = search_name('html', ['&thorn;', 'THORN', '¬anentity'], chars(0, 0xFF))
    assert set(r) == set('þÞ')

def test_search_name_bad():
    with pytest.raises(ValueError, match='Unknown'):
        _ = search_name('bad', ['c[eo]*n'], chars(0, 0x7F))
