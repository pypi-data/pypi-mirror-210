import os
import sys
import re
import types

import string
from datetime import datetime, timedelta
from dateutil import parser
from glom import glom, assign
import jmespath

# --------------------------------------------------
#  Convert Base
# --------------------------------------------------

# CHAR_LOOKUP = list(string.digits + string.ascii_letters)

#  avoid use of numbers (so can be used as regular attribute names with ".")
CHAR_LOOKUP = list(string.ascii_letters)
INV_LOOKUP = {c: i for i, c in enumerate(CHAR_LOOKUP)}


def convert_base(number, base, padding=-1, lookup=CHAR_LOOKUP):
    """Coding a number into a string in base 'base'

    results will be padded with '0' until minimal 'padding'
    length is reached.

    lookup is the char map available for coding.
    """
    if base < 2 or base > len(lookup):
        raise RuntimeError(
            f"base: {base} > coding map length: {len(lookup)}"
        )
    mods = []
    while number > 0:
        mods.append(lookup[number % base])
        number //= base

    while len(mods) < padding:
        mods.append(lookup[0])

    mods.reverse()
    return ''.join(mods)


def from_base(key, base, inv_lookup=INV_LOOKUP):
    """Convert a coded number in base 'base' to an integer."""
    number = 0
    keys = list(key)
    keys.reverse()
    w = 1
    for c in keys:
        number += INV_LOOKUP[c] * w
        w *= base
    return number


# def new_uid(base=50):
# number = uuid.uuid1()
# return convert_base(number.int, base)
SEED = 12345


def new_uid(base=50):
    global SEED
    SEED += 1
    return convert_base(SEED, base)


# SEED = -1

# def new_uid(base=50):
# """test uid generator for debugging"""
# global SEED
# known = ['control', 'analysis', 'tech', 'doc', 'web', 'dep']
# SEED += 1
# if SEED < len(known):
# return known[SEED]

# return convert_base(12345 + SEED, base)


# from xml.sax.saxutils import escape
# ------------------------------------------------
# jinja2 filters
# ------------------------------------------------
def escape(text: str):
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    text = text.replace("\"", "&quot;")
    text = text.replace("'", "&apos;")
    return text


def fmt(value, fmt=">40"):
    fmt = "{:" + fmt + "}"
    try:
        value = fmt.format(value)
    except:
        pass
    return value


def xp(data, spec):
    if hasattr(data, '__len__'):
        data = list(data)
    return jmespath.search(spec, data)


# ------------------------------------------------
# glom extensions
# ------------------------------------------------
def setdefault(obj, path, val, missing=dict):
    current = glom(obj, path, default=None)
    if current is None:
        assign(obj, path, val, missing=missing)
        return val
    return current


# ------------------------------------------------
# Converter functions
# ------------------------------------------------
def I(x):
    return x


def INT(x):
    return int(x)


def FLOAT(x):
    return float(x)


def BOOL(x):
    return x.lower() in ('true', 'yes')


def TEXT(x):
    return x.text


def DATE(x):  # TODO
    return parser.parse(x)


def DURATION(x):  # TODO
    return timedelta(days=float(x))


def COLOR(x):
    """Task color
    Ignore when if a "black" or "blue" color and let GP
    use default ones next time.
    """
    if x not in ('#8cb6ce', '#000000'):
        return x
    return x  # TODO: remove, this hack will remove default colors


def PRIORITY(x):
    """GanttProject PRIORITY.... (have not sense :) )"""
    return {
        '3': -2,  #  Lowest
        '0': -1,  #  Low
        None: 0,  #  Normal (missing)
        '2': 1,  #  High
        '4': 2,  #  Highest
    }.get(x, 0)


# ------------------------------------------------
# console
# ------------------------------------------------

GREEN = "\033[32;1;4m"
RESET = "\033[0m"


def banner(
    header,
    lines=None,
    spec=None,
    sort_by=None,
    sort_reverse=True,
    output=print,
):
    lines = lines or []
    # compute keys spaces
    m = 1 + max([len(k) for k in lines] or [0])
    if isinstance(lines, dict):
        if sort_by:
            idx = 0 if sort_by.lower().startswith('keys') else 1
            lines = dict(
                sorted(
                    lines.items(),
                    key=lambda item: item[idx],
                    reverse=sort_reverse,
                )
            )
        _lines = []
        for k, v in lines.items():
            if spec:
                try:
                    v = glom(v, spec)
                except:
                    v = getattr(v, spec)

            line = f"{k.ljust(m)}: {v}"
            _lines.append(line)
        lines = _lines

    m = max([len(l) for l in lines] or [40, len(header)]) - len(header) + 1
    output(f"{GREEN}{header}{' ' * m}{RESET}")
    for line in lines:
        output(line)


if __name__ == '__main__':
    foo = 1
