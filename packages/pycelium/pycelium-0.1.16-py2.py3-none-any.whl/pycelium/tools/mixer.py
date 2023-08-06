"""Merge yaml documents, inspired in HELM charts.
"""
from functools import partial
import os
import yaml

# import ruamel.yaml as yaml

from jinja2 import Environment, FileSystemLoader

from .cli.config import PINK, BLUE, YELLOW, RESET
from .persistence import find_files
from .templating import find
from .containers import merge
from .helpers import banner
from ..tools import expandpath


def save_yaml(data, path):
    if not os.path.splitext(path)[-1]:
        path = f"{path}.yaml"

    path = expandpath(path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    yaml.dump(data, open(path, "w"), Dumper=yaml.Dumper)


def merge_yaml(folders, **kw):
    """Merge many yaml documents into a single one.
    - find files recursively
    - merge by alphabetic order
    - expand yaml files agains jinja2 template engine
    """

    T_DIR = './templates'
    ENV = Environment(
        extensions=['jinja2.ext.do'],
        loader=FileSystemLoader(T_DIR),
        auto_reload=True,
    )

    kw['ENV'] = ENV

    _find = partial(find, **kw)
    ENV.filters['find'] = _find

    # include 'extensions'
    kw.setdefault('find', _find)

    # start rendering
    result = {}
    found = find_files(folders, sort_by="keys", match=True, **kw)
    banner("Found", found)
    banner("Loading")

    for i, path in enumerate(found):
        source = open(path).read()
        template = ENV.from_string(source, globals=kw)
        output = template.render(**kw)

        print(f"{PINK}---> {path}{RESET}")
        print(output)
        # print(f"{PINK}<--- {RESET}")
        foo = 1

        for j, data in enumerate(yaml.load_all(output, Loader=yaml.Loader)):
            print(f"{YELLOW}- [{i}].{j}: {path}{RESET}")
            merge(result, data, inplace=True)

    return result
