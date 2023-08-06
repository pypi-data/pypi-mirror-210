import asyncio
import re
import os
import click

from pycelium.action import Action
from pycelium.installer import Installer
from pycelium.shell import Reactor, DefaultExecutor
from pycelium.rsync import Rsync  # forced import (late-binding)

# from pycelium.pastor import Pastor
# from pycelium.scanner import Settler

from pycelium.tools import soft, expandpath, parse_uri
from pycelium.tools.persistence import find_files
from pycelium.tools.cli.inventory import (
    inventory,
    credentials,
    INVENTORY_ROOT,
    explore_host,
    get_mac,
    get_host_tags,
    save_yaml,
)
from pycelium.tools.cli.config import (
    config,
    banner,
    RESET,
    BLUE,
    PINK,
    YELLOW,
    GREEN,
)
from ..tools import extend_config, build_deltas, analyze_args


@inventory.command()
# @click.argument('filename', default='sample.gan')
@click.option("--network", multiple=True)
@click.option("--user", multiple=True)
@click.option("--password", multiple=True)
@click.option("--shuffle", default=False, type=bool)
@click.pass_obj
def install(env, network, user, shuffle, password):
    """
    - [ ] Gather information similar as explore
    - [ ] Install single node
    """
    config.callback()
    extend_config(env)

    conquered = dict()
    cfg = dict(env.__dict__)

    top = expandpath(INVENTORY_ROOT)
    print(f"network: {network}")
    print(f"user: {user}")
    for ctx in credentials(network, user, shuffle, password, cfg):
        soft(ctx, **cfg)
        print("{_progress:.2%} {_printable_uri:>40}".format_map(ctx))
        host = ctx['host']
        if host in conquered:
            print(f"{host} is alredy conquered! :), skiping")
            continue

        data = explore_host(ctx)
        mac = get_mac(data)
        if mac:
            mac = mac.replace(':', '')
            ctx['observed_hostname'] = observed_hostname = (
                data.get('observed_hostname') or host
            )
            data = data.get('real')
            tags = get_host_tags(data)
            _tags = '/'.join(tags)
            path = f"{top}/{_tags}/{observed_hostname}.{mac}.yaml"
            print(f"saved: {path}")

            save_yaml(data, path)
            conquered[host] = data
            conquered[observed_hostname] = data

            # now the install part
            tags.add(observed_hostname)
            install_single_node(tags, ctx)
            foo = 1

    foo = 1


def install_single_node(tags, ctx):
    includes = ctx.get('includes', [])

    tags.add('base')
    for t in tags:
        for t in re.findall(r'\w+', t):
            includes.append(f'(.*?\.)?{t}\.yaml')

    reactor = Reactor(env=ctx)

    conn = DefaultExecutor(**ctx)
    reactor.attach(conn)

    # stm = Settler(daemon=False)
    stm = Installer(daemon=False)
    reactor.attach(stm)

    # magic ...
    asyncio.run(reactor.main())

    foo = 1


@inventory.command()
# @click.argument('filename', default='sample.gan')
@click.option("--target", default='./templates')
@click.option("--source", default='~')
@click.option(
    "--include", default='wireguard/.*?/(?P<name>(?P<host>venoen\d+).conf)'
)
@click.option(
    "--pattern", default='{target}/{host}/wireguard/wg-centesimal.conf'
)
@click.option("--overwrite", is_flag=True, default=False)
@click.pass_obj
def cpwireguard(env, target, source, include, pattern, overwrite):
    """Copy WG config files from other locations"""
    config.callback()
    folders = [source]
    includes = [include]

    found = find_files(
        folders=folders,
        includes=includes,
    )

    for i, path in enumerate(found):
        print(f"{PINK}---> {path}{RESET}")
        for reg in includes:
            m = re.search(reg, path)
            if m:
                d = m.groupdict()
                d['target'] = target
                dest = pattern.format_map(d)
                if os.path.exists(dest) and not overwrite:
                    print(f"Skipping: {dest}, already exists")
                    continue

                print(dest)
                text = open(path).read()
                # print(text)
                text = translate_wg_config(text)
                # print(text)
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                open(dest, 'wt').write(text)

                foo = 1

    foo = 1


def translate_wg_config(text):
    rules = {
        r'(Address\s+=\s+[\d\.]+)(/16)': r'\1/32',
        r'(AllowedIPs\s+=\s+10.220)(.2.33)/(16|32)': r'\1.0.0/16',
    }
    for pattern, repl in rules.items():
        text = re.sub(pattern, repl, text)

    return text


@inventory.command()
# @click.argument('filename', default='sample.gan')
@click.option("--source", default='./templates')
@click.option("--uri", default='agp@wsentinel:~/workspace/iot/templates')
@click.pass_obj
def rsync(env, source, uri):
    """Copy WG config files from other locations"""
    config.callback()
    analyze_args(env, uri)

    ctx = env.__dict__

    # folders = [source]
    # includes = [include]

    # found = find_files(
    # folders=folders,
    # includes=includes,
    # )

    # includes = ctx.get('includes', [])

    # tags.add('base')
    # for t in tags:
    # for t in re.findall(r'\w+', t):
    # includes.append(f'(.*?\.)?{t}\.yaml')

    reactor = Reactor(env=ctx)

    conn = DefaultExecutor(**ctx)
    reactor.attach(conn)

    # stm = Settler(daemon=False)
    stm = Dummy(source=source, target=uri)
    reactor.attach(stm)

    # magic ...
    asyncio.run(reactor.main())


class Dummy(Action):
    """ """

    def __init__(self, source, target, *args, **kw):
        self._stop_no_seq = False  # wait until fibers have done
        super().__init__(*args, **kw)
        self.source = source
        self.target = target
        foo = 1

    # --------------------------------------------------
    # Coded as sequence: # TODO: review
    # --------------------------------------------------
    async def _seq_10_rsync_remote(self, *args, **kw):
        executor = await self.is_connected()
        result = await executor.rsync(self.source, self.target)

        return True
