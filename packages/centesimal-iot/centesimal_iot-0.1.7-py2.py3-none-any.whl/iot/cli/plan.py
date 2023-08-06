import time
import os
import re
import yaml

# import ruamel.yaml as yaml

import asyncio

from datetime import datetime
from glom import glom, assign

import click

from pycelium.shell import Reactor, DefaultExecutor
from pycelium.pastor import Pastor
from pycelium.scanner import Settler

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

from ..tools import extend_config, build_deltas, analyze_args
from .target import target
from .real import real


@main.group(context_settings=CONTEXT_SETTINGS)
@click.pass_obj
def plan(env):
    # banner("User", env.__dict__)
    pass


@plan.command()
# @click.argument('filename', default='sample.gan')
@click.option("--email", default=None)
@click.option("--cost", default=30)
@click.pass_obj
def new(env, email, cost=0):
    raise NotImplementedError("not yet!")


@plan.command()
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


@plan.command()
@click.option("--uri", default=None)
@click.option("--include", multiple=True)
@click.option("--output", default=True, type=bool)
@click.option("--tag", multiple=True)
@click.pass_obj
def apply(env, uri, include, output, tag):
    config.callback()
    analyze_args(env, uri, include, output, tag)

    ctx = dict(env.__dict__)

    reactor = Reactor(env=ctx)
    conn = DefaultExecutor(**ctx)
    reactor.attach(conn)

    # stm = Settler(daemon=False)
    stm = Pastor(daemon=False)
    reactor.attach(stm)

    # magic ...
    asyncio.run(reactor.main())
