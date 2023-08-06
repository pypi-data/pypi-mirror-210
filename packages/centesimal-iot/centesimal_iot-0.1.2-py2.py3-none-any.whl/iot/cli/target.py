import time
import os
import sys
import yaml

# import ruamel.yaml as yaml

from datetime import datetime
from glom import glom, assign

import click

from pycelium.tools import parse_uri, build_uri
from pycelium.tools.cli.main import main, CONTEXT_SETTINGS
from pycelium.tools.cli.config import config, banner, RED

from pycelium.tools.containers import walk
from pycelium.tools.mixer import merge_yaml
from pycelium.tools.persistence import find_files
from pycelium.tools.persistence import find_data_files, SORT_PATTERN
from pycelium.tools.templating import load_yaml, decode_dict_new_lines


from ..tools import extend_config


@main.group(context_settings=CONTEXT_SETTINGS)
@click.pass_obj
def target(env):
    # banner("User", env.__dict__)
    pass


@target.command()
# @click.argument('filename', default='sample.gan')
@click.option("--email", default=None)
@click.option("--cost", default=30)
@click.pass_obj
def new(env, email, cost=0):
    raise NotImplementedError("not yet!")


@target.command()
@click.option("--uri", default="localhost")
@click.option("--path", default=None)
@click.pass_obj
def test(env, uri, path):
    config.callback()
    extend_config(env)
    ctx = parse_uri(uri, **env.__dict__)

    if not path:
        path = "{target}/{host}.yaml".format_map(ctx)

    try:
        result = load_yaml(path)
        banner("output")
        print(yaml.dump(result))

    except Exception as why:
        banner("output", color=RED)
        print(why)
        sys.exit(1)

    foo = 1


@target.command()
@click.option("--uri", default="localhost")
@click.option("--include", default=None)
@click.pass_obj
def list(env, uri, include):
    config.callback()
    extend_config(env)
    # ctx = parse_uri(uri, **env.__dict__)

    folders = env.target
    include = include if include is not None else ".*\.yaml$"
    result = find_data_files(folders, includes=include)
    banner(f"Found: ({len(result)}) files in {folders}", result)
    return result


@target.command()
@click.option("--uri", default="localhost")
@click.option("--include", default=None)
@click.option("--output", default=None)
@click.pass_obj
def build(env, uri, include, output):
    config.callback()
    extend_config(env)
    ctx = parse_uri(uri, **env.__dict__)

    if include:
        ctx["includes"] = include
    result = merge_yaml(sort_pattern=SORT_PATTERN, **ctx)

    if output:
        yaml.dump(result, open(output, "w"))
    else:
        banner("output")
        print(yaml.dump(result))

    # check
    if env.debug:
        # check that we can save and load yaml format file
        path = f"/tmp/{time.time()}.yaml"
        yaml.dump(result, open(path, "w"))

        # check that we can decode multiline values from loaded file
        # dummy = yaml.load(open(path), Loader=yaml.Loader)
        # decode_dict_new_lines(dummy)

        dummy = load_yaml(path)
        for key, value in walk(dummy):
            if key and key[-1] in ("content",):
                # value = value.replace("\\n", "\n")
                print("." * 80)
                print(f"checking {key} conversion")
                print("." * 80)
                print(value)
                assert "\\n" not in value

        os.unlink(path)

    return result
