# SPDX-License-Identifier: MIT
"""Character name searches."""

import fnmatch
import re
import unicodedata

from collections.abc import Callable, Iterable
from typing import Any

import uc.html
import uc.uni

# Name searches.

NameSearch = Callable[
    [Iterable[str], Iterable[str], Callable[[Iterable], bool]], Iterable[str]]

Fold = Callable[[Iterable[Any]], bool]

def search_exact(select: Iterable[str],
                 source: Iterable[str],
                 _fold: Fold = all) -> Iterable[str]:
    r = []
    for s in select:
        if len(s) == 1:
            c = s
        else:
            try:
                c = uc.uni.unichr(s)
            except ValueError:
                continue
        if c in source:
            r.append(c)
    return r

def search_match(select: Iterable[str],
                 source: Iterable[str],
                 fold: Fold = all) -> Iterable[str]:
    search = [s.upper() for s in select]
    return (c for c in source if fold(
        x in unicodedata.name(c, '') for x in search))

def search_word(select: Iterable[str],
                source: Iterable[str],
                fold: Fold = all) -> Iterable[str]:
    search = [s.upper() for s in select]
    return (c for c in source if fold(
        x in unicodedata.name(c, '').split() for x in search))

def search_egrep(select: Iterable[str],
                 source: Iterable[str],
                 fold: Fold = all) -> Iterable[str]:
    search = [re.compile(x, re.IGNORECASE) for x in select]
    return (c for c in source if fold(
        x.search(unicodedata.name(c, '')) for x in search))

def search_glob(select: Iterable[str],
                source: Iterable[str],
                fold: Fold = all) -> Iterable[str]:
    return search_egrep((fnmatch.translate(x) for x in select), source, fold)

def search_html(select: Iterable[str],
                source: Iterable[str],
                _fold: Fold = all) -> Iterable[str]:
    r: list[str] = []
    for s in select:
        if (ec := uc.html.entity_to_characters(s)):
            r += ec
    return (c for c in source if c in r)

__NAME_SEARCH = {
    'exact': search_exact,
    'match': search_match,
    'word': search_word,
    'egrep': search_egrep,
    'glob': search_glob,
    'html': search_html,
}

def search_name(mode: str,
                select: Iterable[str],
                source: Iterable[str],
                fold: Fold = all) -> Iterable[str]:
    if mode in __NAME_SEARCH:
        return __NAME_SEARCH[mode](select, source, fold)
    message = f'Unknown mode ‘{mode}’'
    raise ValueError(message)
