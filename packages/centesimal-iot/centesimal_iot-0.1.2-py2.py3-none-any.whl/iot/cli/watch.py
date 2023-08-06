import time
import os

import yaml

# import ruamel.yaml as yaml

import asyncio

from datetime import datetime
from glom import glom, assign

import click

from pycelium.shell import Reactor, DefaultExecutor
from pycelium.pastor import Pastor
from pycelium.pastor import Pastor

from pycelium.tools import parse_uri, build_uri
from pycelium.tools.cli.main import main, CONTEXT_SETTINGS
from pycelium.tools.cli.config import (
    config,
    banner,
    RESET,
    BLUE,
    PINK,
    YELLOW,
    GREEN,
)

from pycelium.definitions import REAL, TARGET
from pycelium.tools.containers import walk, diff, chop, get_deltas, bspec
from pycelium.tools.mixer import merge_yaml, save_yaml
from pycelium.tools.persistence import find_files
from pycelium.tools.persistence import find_data_files, SORT_PATTERN
from pycelium.tools.templating import decode_dict_new_lines
from pycelium.watch import WatchDog

from ..tools import extend_config, build_deltas
from .target import target
from .real import real


@main.group(context_settings=CONTEXT_SETTINGS)
@click.pass_obj
def watch(env):
    # banner("User", env.__dict__)
    pass


@watch.command()
# @click.argument('filename', default='sample.gan')
@click.option("--email", default=None)
@click.option("--cost", default=30)
@click.pass_obj
def new(env, email, cost=0):
    raise NotImplementedError("not yet!")


@watch.command()
@click.option("--uri", default="localhost")
@click.option("--include", default=None)
@click.pass_obj
def show(env, uri, include):
    config.callback()
    extend_config(env)
    ctx = parse_uri(uri, **env.__dict__)

    result = build_deltas(include, **ctx)

    banner(f"Found: ({len(result)}) deltas")
    print(f"{RESET}")

    for i, (key, old, new) in enumerate(get_deltas(result)):
        key = "".join([f"[{k}]" for k in key])
        old = str(old)
        new = str(new)
        print(f"[{i}] : {key:<60}: {old:<10} --> {new:<10}")

    return result


@watch.command()
@click.option("--uri", default="localhost")
@click.option("--include", multiple=True)
@click.option("--output", default=None)
@click.pass_obj
def network(env, uri, include, output):
    config.callback()
    extend_config(env)
    ctx = parse_uri(uri, **env.__dict__)
    if isinstance(include, str):
        include = include.split(",")
    elif not include:
        include = [
            p.format_map(ctx)
            for p in [
                "{host}\.yaml",
                "specs\.yaml",
            ]
        ]
    else:
        include = list(include)

    ctx["includes"] = include
    ctx["folders"] = ctx["target"]
    target = merge_yaml(sort_pattern=SORT_PATTERN, **ctx)

    if output:
        if not os.path.splitext(output)[-1] and output.lower() in (
            'yes',
            'true',
        ):
            output = f"output/{ctx['host']}.yaml"

        save_yaml(target, output)

    # banner(f"Found: ({len(result)}) deltas")
    # print(f"{RESET}")

    reactor = Reactor(env=ctx)
    conn = DefaultExecutor(**ctx)
    reactor.attach(conn)

    stm = WatchDog()
    reactor.attach(stm)

    # set target state
    # (reload load in idle events)
    # spec = bspec(TARGET)
    # assign(reactor.ctx, spec, target, missing=dict)

    # magic ...
    asyncio.run(reactor.main())
