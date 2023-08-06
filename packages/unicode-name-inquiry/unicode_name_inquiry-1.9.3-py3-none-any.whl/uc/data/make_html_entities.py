# SPDX-License-Identifier: MIT
"""Generate html_entities.py."""

import argparse
import datetime
import json
import pathlib
import sys

from pathlib import Path

PREFER = [
    'aleph',
    'and',
    'hbar',
    'notin',
    'or',
]

def preferred(a: str, b: str) -> tuple[str, str]:
    if not b.islower() or b[0] == 'x' or a in PREFER:
        return a, b
    if not a.islower() or a[0] == 'x' or b in PREFER:
        return b, a
    if len(a) > len(b):
        return a, b
    return b, a

def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv
    cmd = pathlib.Path(argv[0]).stem
    parser = argparse.ArgumentParser(
        prog=cmd, description='Generate ISBN ranges')
    parser.add_argument(
        '--input',
        '-i',
        metavar='FILE',
        default='third_party/whatwg/entities.json',
        help='Input file.')
    parser.add_argument(
        '--output',
        '-o',
        metavar='FILE',
        default='src/uc/data/html_entities.py',
        help='Output file.')
    args = parser.parse_args(argv[1 :])

    with Path(args.input).open('r', encoding='utf-8') as f:
        j = json.load(f)

    ed: dict[str, str] = {}
    xd: dict[str, str] = {}
    entities = []
    for e, cc in j.items():
        entity = e.removeprefix('&').removesuffix(';')
        if (ch := cc.get('characters')) is None:
            continue
        if len(ch) != 1:
            xd[entity] = ch
            continue
        if ch in ed:
            if ch == ed[ch]:
                continue
            entity, other = preferred(entity, ed[ch])
            xd[other] = ch
        ed[ch] = entity
        entities.append(entity)

    with pathlib.Path(args.output).open('w', encoding='utf-8') as f:
        f.write('"""Generated HTML entity data."""\n\n')
        f.write('# DO NOT EDIT!\n')
        f.write(f'# Generated from {args.input}\n')
        f.write(
            f'# at {datetime.datetime.now(tz=datetime.UTC).isoformat()}\n\n')
        f.write('HTML_ENTITY = {\n')
        for ch in sorted(ed.keys()):
            f.write(f'{ch!r}: {ed[ch]!r},\n')
        f.write('}\n\n')
        f.write('OTHER = {\n')
        for entity in sorted(xd.keys()):
            if entity not in entities:
                f.write(f'{entity!r}: {xd[entity]!r},\n')
        f.write('}\n\n')

    return 0

if __name__ == '__main__':
    sys.exit(main())
