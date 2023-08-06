import re
import os
import yaml

import asyncio
from datetime import datetime
from glom import glom

import click

from pycelium.shell import Reactor, DefaultExecutor
from pycelium.pastor import Pastor

from pycelium.tools.cli.main import main, CONTEXT_SETTINGS
from pycelium.tools.cli.config import config, banner
from pycelium.tools.cli.run import run

from pycelium.tools.mixer import merge_yaml
from pycelium.tools.persistence import find_files


@run.command()
# @click.argument('filename', default='sample.gan')
@click.option("--host", default="localhost")
@click.pass_obj
def check(env, host, cost=0):
    config.callback()

    reactor = Reactor()
    conn = DefaultExecutor(host=host)
    reactor.attach(conn)

    stm = Pastor()
    reactor.attach(stm)

    asyncio.run(reactor.main())

    foo = 1
