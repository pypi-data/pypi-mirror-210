# SPDX-License-Identifier: MIT
"""Test uc.html."""

# Want to test explicit results.
# ruff: noqa: PLC1901

import uc.html

def test_html_character_to_entity():
    assert uc.html.character_to_entity('B') == '&#0042;'
    assert uc.html.character_to_entity('\u00FE') == '&thorn;'

def test_html_entity_to_characters():
    assert uc.html.entity_to_characters('&#0042;') == 'B'
    assert uc.html.entity_to_characters('#0042;') == 'B'
    assert uc.html.entity_to_characters('&#0042') == 'B'
    assert uc.html.entity_to_characters('#0042') == 'B'
    assert uc.html.entity_to_characters('&thorn;') == '\u00FE'
    assert uc.html.entity_to_characters('thorn') == '\u00FE'
    assert uc.html.entity_to_characters('thorn') == '\u00FE'
    assert uc.html.entity_to_characters('Aacute') == '\u00C1'
    assert uc.html.entity_to_characters('thickapprox') == '\u2248'
    assert uc.html.entity_to_characters('&asymp;') == '\u2248'
    assert uc.html.entity_to_characters('&lesg;') == '\u22DA\uFE00'

def test_html_entity_to_character_fail():
    assert uc.html.entity_to_characters('&notanhtmlentity;') == ''
    assert uc.html.entity_to_characters('&#0M42;') == ''
