import re
import os
import sys
import time
import yaml

from asyncio import run
from datetime import datetime

import click

from glom import glom

from pycelium.shell import Reactor, DefaultExecutor
from pycelium.pastor import Pastor
from pycelium.scanner import Settler

from pycelium.tools import parse_uri, build_uri
from pycelium.tools.cli.main import main, CONTEXT_SETTINGS
from pycelium.tools.cli.config import config, banner, RED
from pycelium.tools.mixer import merge_yaml
from pycelium.tools.persistence import find_files
from pycelium.tools.persistence import find_data_files, SORT_PATTERN
from pycelium.tools.templating import load_yaml, decode_dict_new_lines

from ..tools import extend_config


@main.group(context_settings=CONTEXT_SETTINGS)
@click.pass_obj
def real(env):
    # banner("User", env.__dict__)
    pass


@real.command()
@click.option("--uri", default="localhost")
@click.option("--output", default=None)
@click.option("--force", default=False)
@click.pass_obj
def get(env, uri, output, force):
    config.callback()
    extend_config(env)
    ctx = parse_uri(uri, **env.__dict__)

    if not output:
        output = "{real}/{host}.yaml".format_map(ctx)
        # output = output or f"{ctx.get('host')}.yaml"

    if os.path.exists(output) and not force:
        banner("Error: File exist", color=RED)
        print(f"{output}")
        print("user --force=True to overwrite file")
        sys.exit(1)

    host = ctx["host"]

    banner(f"Facts from '{host}'")

    reactor = Reactor()
    conn = DefaultExecutor(**ctx)
    reactor.attach(conn)

    stm = Settler(daemon=False)
    reactor.attach(stm)

    run(reactor.main())

    if output:
        reactor.save(output)
    else:
        # dump yaml to console
        path = f"/tmp/{time.time()}.yaml"
        reactor.save(path)

        banner("output")
        print(open(path).read())
        os.unlink(path)

    foo = 1


@real.command()
@click.option("--uri", default="localhost")
@click.option("--path", default=None)
@click.pass_obj
def test(env, uri, path):
    config.callback()
    extend_config(env)
    ctx = parse_uri(uri, **env.__dict__)

    if not path:
        path = "{real}/{host}.yaml".format_map(ctx)

    try:
        result = load_yaml(path)
        banner("output")
        print(yaml.dump(result))

    except Exception as why:
        banner("output", color=RED)
        print(why)
        sys.exit(1)

    foo = 1


@real.command()
@click.option("--uri", default="localhost")
@click.option("--include", default=None)
@click.pass_obj
def list(env, uri, include):
    config.callback()
    extend_config(env)
    ctx = parse_uri(uri, **env.__dict__)

    # ctx['folders'] = env.real
    folders = env.real
    include = include if include is not None else ".*\.yaml$"
    found = find_data_files(folders, includes=include)
    banner(f"Found: ({len(found)}) files in {folders}", found)
    foo = 1
