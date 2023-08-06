import yaml

from jinja2 import Environment, FileSystemLoader
from glom import assign

from .persistence import find_files, basic_info
from .containers import bspec, search


# ------------------------------------------------
# locate files
# ------------------------------------------------
def find(pattern, **ctx):
    ENV = ctx.get("ENV")
    if not ENV:
        ENV = Environment(
            extensions=["jinja2.ext.do"],
            loader=FileSystemLoader("."),
            auto_reload=True,
        )

    folders = ctx.get("templates", ".")

    template = ENV.from_string(pattern, globals=ctx)
    _pattern = template.render(**ctx)
    includes = _pattern

    found = find_files(
        folders,
        includes=includes,
        info_callback=basic_info,
        sort_by="keys",
    )
    for path, item in found.items():
        item["raw"] = raw = open(path).read()

        # if binary file?
        for c in raw[:1024]:
            o = ord(c)
            if not (o >= 32 or o in (10, 13)):
                break
        else:  # file content is ASCII
            render = ENV.from_string(raw).render(item=item, **ctx)
            if "\n" in render:
                # render = "|" + "\n" + render
                render = encode_new_lines(render)
                foo = 1
            item["render"] = render

        yield item


# ------------------------------------------------
# encode / decode yaml files
# ------------------------------------------------
def encode_new_lines(value):
    value = value.replace("\n", "\\n")
    value = f"'{value}'"
    return value


def decode_new_lines(value):
    value = value.replace("\\n", "\n")
    return value


def decode_dict_new_lines(result):
    blueprint = {
        ".*(content|text)": r".*\\n.*",
    }

    modify = search(result, blueprint, flat=True)
    for key, value in modify.items():
        value = decode_new_lines(value)
        spec = bspec(key)
        assign(result, spec, value)


def encode_dict_new_lines(result):
    blueprint = {
        ".*(content|text)": r".*\n.*",
    }

    modify = search(result, blueprint, flat=True)
    for key, value in modify.items():
        value = encode_new_lines(value)
        spec = bspec(key)
        assign(result, spec, value)


# ------------------------------------------------
# load and decoce yaml
# ------------------------------------------------
def load_yaml(path):
    result = yaml.load(open(path).read(), Loader=yaml.Loader)
    decode_dict_new_lines(result)
    return result
