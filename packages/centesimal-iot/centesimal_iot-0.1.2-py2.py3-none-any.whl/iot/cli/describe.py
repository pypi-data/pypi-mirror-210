import os
import yaml
from glom import glom, assign

import click

from pycelium.tools.cli.main import *
from pycelium.tools.helpers import setdefault
from pycelium.tools.helpers import banner as _banner


# https://stackoverflow.com/questions/4842424/list-of-ansi-color-escape-sequences
GREEN = "\033[32;1;4m"
RESET = "\033[0m"


def load_config(env):
    env.__dict__.update(
        yaml.load(open(env.config_file, 'rt'), Loader=yaml.Loader)
    )


def save_config(env):
    os.makedirs(os.path.dirname(env.config_file), exist_ok=True)
    yaml.dump(env.__dict__, open(env.config_file, 'wt'))


def banner(header, lines, spec=None, sort_by=None, sort_reverse=True):
    _banner(header, lines, spec, sort_by, sort_reverse, output=click.echo)


@main.group(context_settings=CONTEXT_SETTINGS)
@click.pass_obj
def describe(env):
    # click.echo(f"Env: {env.__dict__}/")
    env.config_file = os.path.join(env.home, 'config.yaml')
    try:
        load_config(env)
        # setdefault(env, 'ext', '.gan')
        setdefault(
            env,
            'includes',
            {
                '.*\.deploy$': None,
            },
        )
        setdefault(
            env,
            'excludes',
            {},
        )
        setdefault(
            env,
            'folders',
            {
                '~/Documents': None,
            },
        )
        setdefault(
            env,
            'resource',
            os.path.join(env.home, 'resources.yaml'),
        )
        setdefault(
            env,
            'role',
            os.path.join(env.home, 'roles.yaml'),
        )
    except Exception as why:
        print(f"{why}")
        save_config(env)

    save_config(env)
    return env


@config.command()
@click.pass_obj
def list(env):
    banner("Config", env.__dict__)


@config.command()
@click.option('--include', default=None)
@click.option('--exclude', default=None)
@click.option('--folder', default=None)
@click.pass_obj
def view(env, include, exclude, folder):
    if include:
        click.echo(f"add include: {include}")
        s = setdefault(env, 'includes', dict())
        s[include] = None
        save_config(env)
    if exclude:
        click.echo(f"add exclude: {exclude}")
        s = setdefault(env, 'excludes', dict())
        s[exclude] = None
        save_config(env)
    if folder:
        click.echo(f"add folder: {folder}")
        s = setdefault(env, 'folders', dict())
        s[folder] = None
        save_config(env)
    list.callback()


@config.command()
@click.option('--include', default=None)
@click.option('--exclude', default=None)
@click.option('--folder', default=None)
@click.pass_obj
def set_cluster(env, include, exclude, folder):
    if include:
        click.echo(f"add include: {include}")
        s = setdefault(env, 'includes', dict())
        s[include] = None
        save_config(env)
    if exclude:
        click.echo(f"add exclude: {exclude}")
        s = setdefault(env, 'excludes', dict())
        s[exclude] = None
        save_config(env)
    if folder:
        click.echo(f"add folder: {folder}")
        s = setdefault(env, 'folders', dict())
        s[folder] = None
        save_config(env)
    list.callback()


@config.command()
@click.option('--include', default=None)
@click.option('--exclude', default=None)
@click.option('--folder', default=None)
@click.pass_obj
def add(env, include, exclude, folder):
    if include:
        click.echo(f"add include: {include}")
        s = setdefault(env, 'includes', dict())
        s[include] = None
        save_config(env)
    if exclude:
        click.echo(f"add exclude: {exclude}")
        s = setdefault(env, 'excludes', dict())
        s[exclude] = None
        save_config(env)
    if folder:
        click.echo(f"add folder: {folder}")
        s = setdefault(env, 'folders', dict())
        s[folder] = None
        save_config(env)
    list.callback()


@config.command()
@click.option('--pattern', default='*.gan')
@click.pass_obj
@click.pass_context
def delete(ctx, env, pattern):
    click.echo(f"delete pattern: {pattern}/")
    s = setdefault(env, 'include', dict())
    if pattern in s:
        s.pop(pattern)
        save_config(env)
    else:
        click.echo(f"pattern: {pattern} not found")
        list.callback()
        # result = ctx.invoke(list, content=ctx.forward(list))

    foo = 1


@config.command()
@click.option('--include', default=None)
@click.option('--exclude', default=None)
@click.option('--folder', default=None)
@click.pass_obj
def delete(env, include, exclude, folder):
    if include:
        click.echo(f"delete include: {include}")
        s = setdefault(env, 'includes', dict())
        s.pop(include, None)
        save_config(env)
    if exclude:
        click.echo(f"add exclude: {exclude}")
        s = setdefault(env, 'excludes', dict())
        s.pop(exclude, None)
        save_config(env)
    if folder:
        click.echo(f"add folder: {folder}")
        s = setdefault(env, 'folders', dict())
        s.pop(folder, None)
        save_config(env)
    list.callback()
