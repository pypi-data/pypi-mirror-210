import re
import os
import yaml

from datetime import datetime
from glom import glom

import click


from pycelium.tools.cli.main import *
from pycelium.tools.cli.config import config

# from .main import *
# from .config import config

# import planner.cli.config


# from ..planner.plugins.ganttproject import GanttProjectImporter

# from planner.pert import PERT
# from planner.persistence import find_files
# from planner.helpers import banner, setdefault
# from planner.consolidation import (
# consolidate,
# ResourceManager,
# RoleManager,
# )


@main.group(context_settings=CONTEXT_SETTINGS)
@click.pass_obj
def user(env):
    # banner("User", env.__dict__)
    pass


@user.command()
# @click.argument('filename', default='sample.gan')
@click.option('--email', default=None)
@click.option('--cost', default=30)
@click.pass_obj
def merge(env, email, cost=0):
    config.callback()

    found = find_files(
        **env.__dict__,
    )
    banner("Found", found)

    banner(f"Loading users from {len(found)} projects")
    root = consolidate(found, output=click.echo)

    # update loaded resource with 'master' db
    resources = glom(root.ROOT, 'resource')
    mgr = ResourceManager(env)
    mgr.update(resources)
    mgr.save(resources)

    foo = 1


@user.command()
# @click.argument('filename', default='sample.gan')
@click.option('--email', default=None)
@click.option('--cost', default=30)
@click.pass_obj
def list(env, email, cost=0):
    config.callback()

    RES = ResourceManager(env)
    resources = RES.update()

    ROLES = RoleManager(env)
    roles = ROLES.update()

    data = {}
    for uid, res in resources.items():
        role = roles.get(res.function, None)
        line = f"{res.name:20}{role}"
        data[uid] = line

    banner("Found", data)

    foo = 1
