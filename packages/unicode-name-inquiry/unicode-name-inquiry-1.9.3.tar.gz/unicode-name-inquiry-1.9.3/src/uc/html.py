# SPDX-License-Identifier: MIT
"""HTML entities."""

from uc.data.html_entities import HTML_ENTITY, OTHER

__REVERSE = {}

def __init_reverse() -> None:
    for c, e in HTML_ENTITY.items():
        __REVERSE[e] = c

def entity_to_characters(e: str) -> str:
    e = e.removeprefix('&').removesuffix(';')
    if e[0] == '#':
        try:
            return chr(int(e[1:], 16))
        except ValueError:
            return ''
    if e in OTHER:
        return OTHER[e]
    if not __REVERSE:
        __init_reverse()
    return __REVERSE.get(e, '')

def character_to_entity(c: str) -> str:
    e = HTML_ENTITY[c] if c in HTML_ENTITY else f'#{ord(c):04X}'
    return f'&{e};'
