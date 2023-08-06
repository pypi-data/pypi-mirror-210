import re
import os
import yaml

from datetime import datetime
from glom import glom

import click

from .main import main, CONTEXT_SETTINGS
from .config import config, banner
from ..mixer import merge_yaml
from ..persistence import find_files


@main.group(context_settings=CONTEXT_SETTINGS)
@click.pass_obj
def run(env):
    # banner("User", env.__dict__)
    pass


@run.command()
# @click.argument('filename', default='sample.gan')
@click.option("--email", default=None)
@click.option("--cost", default=30)
@click.pass_obj
def foo(env, email, cost=0):
    config.callback()

    found = find_files(
        **env.__dict__,
    )
    banner("Found", found)

    banner(f"Loading users from {len(found)} projects")
    # root = consolidate(found, output=click.echo)

    ## update loaded resource with 'master' db
    # resources = glom(root.ROOT, 'resource')
    # mgr = ResourceManager(env)
    # mgr.update(resources)
    # mgr.save(resources)

    foo = 1


@run.command()
@click.option("--host", default="localhost")
@click.pass_obj
def bar(env, host):
    config.callback()

    import iot

    ctx = {
        "host": host,
    }

    folders = [
        os.path.dirname(iot.__file__),
        ".",
    ]
    # folders = list(iot.__path__) + ["."]
    sort_pattern = [
        "((?P<parent>[^/]+)/)?(?P<basename>[^/]+)$",
    ]
    includes = [".*specs.*.yaml"]

    found = find_files(
        folders,
        includes=includes,
        sort_by="keys",
        sort_pattern=sort_pattern,
        **ctx,
    )
    banner("Found", found)

    foo = 1


@run.command()
@click.option("--host", default="localhost")
@click.pass_obj
def merge(env, host):
    config.callback()

    import iot

    ctx = {
        "host": host,
    }
    folders = [
        os.path.dirname(iot.__file__),
        ".",
    ]
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
