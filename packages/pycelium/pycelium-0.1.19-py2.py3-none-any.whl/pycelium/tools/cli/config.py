import os
import yaml
from glom import glom, assign

import click

from .main import *
from ..helpers import setdefault
from ..helpers import banner as _banner
from ..containers import merge

from .. import expandpath

# https://stackoverflow.com/questions/4842424/list-of-ansi-color-escape-sequences
RED = "\033[31;1;4m"
GREEN = "\033[32;1;4m"
YELLOW = "\033[33;1;4m"
BLUE = "\033[34;1;4m"
PINK = "\033[35;1;4m"

RESET = "\033[0m"


def load_config(env):
    """Merge config files"""
    cfg = env.__dict__
    for path in reversed(env.config_files):
        try:
            data = yaml.load(open(path, "rt"), Loader=yaml.Loader)
            merge(cfg, data, inplace=True)
        except FileNotFoundError:
            pass

    env.folders = {expandpath(p): None for p in env.folders}
    foo = 1


def save_config(env):
    os.makedirs(os.path.dirname(env.config_file), exist_ok=True)
    yaml.dump(env.__dict__, open(env.config_file, "wt"))


def banner(
    header,
    lines=None,
    spec=None,
    sort_by=None,
    sort_reverse=True,
    color=GREEN,
):
    _banner(
        header,
        lines,
        spec,
        sort_by,
        sort_reverse,
        output=click.echo,
        color=color,
    )


@main.group(context_settings=CONTEXT_SETTINGS)
@click.pass_obj
def config(env):
    # click.echo(f"Env: {env.__dict__}/")
    try:
        load_config(env)

    except Exception as why:
        print(f"{why}")

        # old = dict(env.__dict__)
        # setdefault(env, 'ext', '.gan')
        setdefault(
            env,
            "includes",
            {
                "iot/.*\.yaml$": None,
            },
        )
        setdefault(
            env,
            "excludes",
            {},
        )
        setdefault(
            env,
            "folders",  # Not regexp
            {
                #'~/Documents': None,
                #'~/workspace': None,
                ".": None,
            },
        )
        setdefault(
            env,
            "resource",
            os.path.join(env.home, "resources.yaml"),
        )
        setdefault(
            env,
            "role",
            os.path.join(env.home, "roles.yaml"),
        )
        # if old != env.__dict__:
        # save_config(env)

        save_config(env)
    return env


@config.command()
@click.pass_obj
def list(env):
    banner("Config", env.__dict__)


@config.command()
@click.option("--include", default=None)
@click.option("--exclude", default=None)
@click.option("--folder", default=None)
@click.pass_obj
def view(env, include, exclude, folder):
    if include:
        click.echo(f"add include: {include}")
        s = setdefault(env, "includes", dict())
        s[include] = None
        save_config(env)
    if exclude:
        click.echo(f"add exclude: {exclude}")
        s = setdefault(env, "excludes", dict())
        s[exclude] = None
        save_config(env)
    if folder:
        click.echo(f"add folder: {folder}")
        s = setdefault(env, "folders", dict())
        s[folder] = None
        save_config(env)
    list.callback()


@config.command()
@click.option("--include", default=None)
@click.option("--exclude", default=None)
@click.option("--folder", default=None)
@click.pass_obj
def set_cluster(env, include, exclude, folder):
    if include:
        click.echo(f"add include: {include}")
        s = setdefault(env, "includes", dict())
        s[include] = None
        save_config(env)
    if exclude:
        click.echo(f"add exclude: {exclude}")
        s = setdefault(env, "excludes", dict())
        s[exclude] = None
        save_config(env)
    if folder:
        click.echo(f"add folder: {folder}")
        s = setdefault(env, "folders", dict())
        s[folder] = None
        save_config(env)
    list.callback()


@config.command()
@click.option("--include", default=None)
@click.option("--exclude", default=None)
@click.option("--folder", default=None)
@click.pass_obj
def add(env, include, exclude, folder):
    if include:
        click.echo(f"add include: {include}")
        s = setdefault(env, "includes", dict())
        s[include] = None
        save_config(env)
    if exclude:
        click.echo(f"add exclude: {exclude}")
        s = setdefault(env, "excludes", dict())
        s[exclude] = None
        save_config(env)
    if folder:
        click.echo(f"add folder: {folder}")
        s = setdefault(env, "folders", dict())
        s[folder] = None
        save_config(env)
    list.callback()


@config.command()
@click.option("--pattern", default="*.gan")
@click.pass_obj
@click.pass_context
def delete(ctx, env, pattern):
    click.echo(f"delete pattern: {pattern}/")
    s = setdefault(env, "include", dict())
    if pattern in s:
        s.pop(pattern)
        save_config(env)
    else:
        click.echo(f"pattern: {pattern} not found")
        list.callback()
        # result = ctx.invoke(list, content=ctx.forward(list))

    foo = 1


@config.command()
@click.option("--include", default=None)
@click.option("--exclude", default=None)
@click.option("--folder", default=None)
@click.pass_obj
def delete(env, include, exclude, folder):
    if include:
        click.echo(f"delete include: {include}")
        s = setdefault(env, "includes", dict())
        s.pop(include, None)
        save_config(env)
    if exclude:
        click.echo(f"add exclude: {exclude}")
        s = setdefault(env, "excludes", dict())
        s.pop(exclude, None)
        save_config(env)
    if folder:
        click.echo(f"add folder: {folder}")
        s = setdefault(env, "folders", dict())
        s.pop(folder, None)
        save_config(env)
    list.callback()
