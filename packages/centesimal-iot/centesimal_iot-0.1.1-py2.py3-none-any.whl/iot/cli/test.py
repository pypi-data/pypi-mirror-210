import re
import os
import yaml

from asyncio import run, wait, create_task, sleep, FIRST_COMPLETED, Queue
from datetime import datetime
from glom import glom

import click

from pycelium.shell import Reactor, DefaultExecutor
from pycelium.pastor import Pastor

from pycelium.tools.cli.main import main, CONTEXT_SETTINGS
from pycelium.tools.cli.config import config, banner
from pycelium.tools.mixer import merge_yaml
from pycelium.tools.persistence import find_files


@main.group(context_settings=CONTEXT_SETTINGS)
@click.pass_obj
def test(env):
    # banner("User", env.__dict__)
    pass


@test.command()
# @click.argument('filename', default='sample.gan')
@click.option("--host", default="localhost")
@click.pass_obj
def example(env, host, cost=0):
    config.callback()

    reactor = Reactor()
    conn = DefaultExecutor(host=host)
    reactor.attach(conn)

    stm = Pastor()
    reactor.attach(stm)

    run(reactor.main())

    # RES = ResourceManager(env)
    # resources = RES.update()

    # ROLES = RoleManager(env)
    # roles = ROLES.update()

    # data = {}
    # for uid, res in resources.items():
    # role = roles.get(res.function, None)
    # line = f"{res.name:20}{role}"
    # data[uid] = line

    # banner("Found", data)

    foo = 1


@test.command()
# @click.argument('filename', default='sample.gan')
@click.option("--host", default="localhost")
@click.pass_obj
def modem(env, host, cost=0):
    config.callback()

    reactor = Reactor()
    conn = DefaultExecutor(host=host)
    reactor.attach(conn)

    stm = Pastor()
    reactor.attach(stm)

    run(reactor.main())

    # RES = ResourceManager(env)
    # resources = RES.update()

    # ROLES = RoleManager(env)
    # roles = ROLES.update()

    # data = {}
    # for uid, res in resources.items():
    # role = roles.get(res.function, None)
    # line = f"{res.name:20}{role}"
    # data[uid] = line

    # banner("Found", data)

    foo = 1


@test.command()
@click.option("--host", default="localhost")
@click.pass_obj
def merge(env, host):
    config.callback()

    import iot

    ctx = {
        "host": host,
    }
    folders = list(iot.__path__) + ["."]
    sort_pattern = [
        "((?P<parent>[^/]+)/)?(?P<basename>[^/]+)$",
    ]
    includes = [".*specs.*.yaml"]

    result = merge_yaml(
        folders, includes=includes, sort_pattern=sort_pattern, **ctx
    )
    output = yaml.dump(result)

    print(output)
    # raw = result["localhost"]["var"]["fs"]["/etc/wireguard/wg0.conf"]["content"]
    # raw = raw.replace("\\n", "\n")
    # print("." * 80)
    # print(raw)

    foo = 1


@test.command()
@click.option("--host", default="localhost")
@click.pass_obj
def merge(env, host):
    config.callback()

    import iot

    ctx = {
        "host": host,
    }
    folders = list(iot.__path__) + ["."]
    sort_pattern = [
        "((?P<parent>[^/]+)/)?(?P<basename>[^/]+)$",
    ]
    includes = [".*specs.*.yaml"]

    result = merge_yaml(
        folders, includes=includes, sort_pattern=sort_pattern, **ctx
    )
    output = yaml.dump(result)

    print(output)
    # raw = result["localhost"]["var"]["fs"]["/etc/wireguard/wg0.conf"]["content"]
    # raw = raw.replace("\\n", "\n")
    # print("." * 80)
    # print(raw)

    foo = 1
