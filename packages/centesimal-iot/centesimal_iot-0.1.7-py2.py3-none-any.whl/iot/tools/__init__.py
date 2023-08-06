import os
import re
import getpass
import platform

from pycelium.definitions import REAL
from pycelium.tools import parse_uri, soft, xoft
from pycelium.tools.containers import chop, diff
from pycelium.tools.mixer import merge_yaml, save_yaml
from pycelium.tools.persistence import SORT_PATTERN


def extend_config(env, **ctx):
    """Extend the config environment with some files."""
    cfg = env.__dict__

    # folders for searching
    parent = os.path.join(*os.path.split(os.path.dirname(__file__))[:-1])

    for p in [os.path.abspath("."), parent]:
        env.folders[p] = None

    # file pattern of specs

    cfg.setdefault("includes", [])
    cfg.setdefault("real", "./real")
    cfg.setdefault("specs", "./specs")

    xoft(cfg, **ctx)

    foo = 1


def build_deltas(include, **ctx):
    target = build_target(include, **ctx)

    # ctx["includes"] = include
    ctx["folders"] = ctx["real"]
    real = merge_yaml(sort_pattern=SORT_PATTERN, **ctx)

    # remove 'real' prefix, to hasve same starting node structure
    real = chop(real, REAL)

    result = diff(target, real, mode="dict")
    return result


def build_target(include, **ctx):
    if isinstance(include, str):
        include = include.split(",")
    elif not include:
        include = [
            p.format_map(ctx)
            for p in [
                "{host}\.yaml",
                "base\.yaml",
            ]
        ]

    host = ctx.get('host')
    m = re.match(r'(?P<host>(?P<family>[^\d]+)(?P<node_id>\d+))', host)
    if m:
        ctx.update(m.groupdict())
        for pattern in '{family}.yaml', '.*{node_id}.yaml':
            include.append(pattern.format_map(ctx))

    foo = 1

    ctx["includes"] = include
    ctx["folders"] = ctx.get("specs", 'specs')
    target = merge_yaml(sort_pattern=SORT_PATTERN, **ctx)
    return target


def analyze_args(env, uri, include=[], output=True, tag=[]):
    extend_config(env)
    uri = uri or 'localhost'

    ctx = parse_uri(uri, **env.__dict__)
    soft(ctx, user=getpass.getuser(), password='123456', host='localhost')

    # localhost case
    if ctx['host'] in ('127.0.0.1', 'localhost'):
        ctx['host'] = ctx['xhost'] = platform.node()

    for k, v in ctx.items():
        print(f"- {k}: {v}")

    env.__dict__.update(ctx)

    include = list(include)
    for t in tag:
        for t in re.findall(r'\w+', t):
            include.append(f'.*{t}.yaml')

    target = build_target(include, **ctx)

    if output:
        if output == True or (
            not os.path.splitext(output)[-1]
            and output.lower()
            in (
                'yes',
                'true',
            )
        ):
            output = f"output/{ctx['host']}.yaml"

        save_yaml(target, output)
    foo = 1
