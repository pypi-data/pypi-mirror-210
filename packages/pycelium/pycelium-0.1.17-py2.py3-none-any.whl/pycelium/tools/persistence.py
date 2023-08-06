import os
import re
import yaml
import pickle
import lzma as xz

from datetime import datetime

from glom import glom


# ------------------------------------------------
# DB dumpers
# ------------------------------------------------


# def save(data):
# if isinstance(data, Zingleton):
# data = data._instances_()

## TODO: xz
# output = yaml.dump(
# data,
# Dumper=yaml.Dumper,
# default_flow_style=False,
# )
# with open('/tmp/output.yaml', 'w') as f:
# f.write(output)
# with xz.open('/tmp/output.yaml.xz', 'wb') as f:
# f.write(output.encode('utf-8'))

# output = pickle.dumps(
# data,
# protocol=-1,
# )
# with open('/tmp/output.pickle', 'wb') as f:
# f.write(output)
# with xz.open('/tmp/output.pickle.xz', 'wb') as f:
# f.write(output)


def load():
    # data = yaml.load(
    # open('/tmp/output.yaml', 'rb'),
    # Loader=yaml.Loader,
    # )
    data = pickle.load(
        xz.open("/tmp/output.pickle.xz", "rb"),
    )
    # provide _uid fiels for most collections
    for kind in "project", "task", "resource":
        collection = glom(data, f"{kind}", default=None)
        if collection:
            for uid, item in collection.items():
                item._uid = uid
    return data


# ------------------------------------------------
#  Persistence
# ------------------------------------------------
class iPersistent:
    def __init__(self, **kw):
        foo = 1

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state):
        self.__dict__.update(state)


class iLoader:
    @classmethod
    def load(cls, folders, includes=[], excludes=[]):
        for path in find_files(
            folders, includes=includes, excludes=excludes
        ):
            data = yaml.load(open(path, "r"), Loader=yaml.Loader)
            yield path, data


# ------------------------------------------------
# locate files
# ------------------------------------------------
HUMAN_SIZE = {
    1024 * 1024: "MB",
    1024: "KB",
    1: "bytes",
}


def to_human(size):
    for block, label in HUMAN_SIZE.items():
        n = size / block
        if n > 1.0:
            if label not in ("B", "bytes"):
                size = f"{n:0.1f} {label}"
            else:
                size = f"{n:0.0f} {label}"

            break
    return size


def ts(path):
    info = basic_info(path)

    date = datetime.utcfromtimestamp(info["mtime"]).strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    size = to_human(info["size"])

    return f"{size:>15}, {date}"


def basic_info(path):
    stats = os.stat(path, follow_symlinks=True)
    info = {
        "ts": datetime.utcfromtimestamp(stats.st_mtime).strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "path": path,
        "name": os.path.splitext(os.path.basename(path))[0],
        "basename": os.path.basename(path),
        "dirname": os.path.dirname(path),
        "mtime": stats.st_mtime,
        "atime": stats.st_atime,
        "ctime": stats.st_ctime,
        "size": stats.st_size,
        "uid": stats.st_uid,
        "gid": stats.st_gid,
        "mode": stats.st_mode,
    }
    return info


def find_files(
    folders,
    includes=[],
    excludes=[],
    sort_by="keys",  # | values
    sort_reverse=False,
    sort_pattern=".*",
    info_callback=ts,
    match=False,
    **kw,
):
    if match:
        search = re.match
    else:
        search = re.search
    found = {}
    if isinstance(folders, str):
        folders = [folders]
    if isinstance(includes, str):
        includes = [includes]
    if isinstance(excludes, str):
        excludes = [excludes]
    if isinstance(sort_pattern, str):
        sort_pattern = [sort_pattern]
    for top in folders:
        top = os.path.expandvars(top)
        top = os.path.expanduser(top)
        top = os.path.abspath(top)
        for root, folders, files in os.walk(top):
            for file in files:
                path = os.path.join(root, file)
                # print(f"debug: {path}")
                ok = False
                for pattern in includes:
                    if search(
                        pattern, file, flags=re.I | re.DOTALL
                    ) or search(pattern, path, flags=re.I | re.DOTALL):
                        ok = True
                        break
                if ok:
                    for pattern in excludes:
                        if search(
                            pattern, file, flags=re.I | re.DOTALL
                        ) or search(pattern, path, flags=re.I | re.DOTALL):
                            ok = False
                            break
                if ok:
                    found[path] = info_callback(path)

    # banner("Found", found, 'st_mtime')
    # sort found files by 'path' (keys) or values ('dates')
    idx, rev = (
        (0, False) if sort_by.lower().startswith("keys") else (1, True)
    )

    def criteria(x):
        for pattern in sort_pattern:
            m = re.search(pattern, x)
            if m:
                # print(f"debug:{x}")
                # print(f"debug: {m.group()}")
                # print(f"debug: {m.groupdict()}")
                return m.group()

    found = dict(
        sorted(
            found.items(),
            key=lambda item: criteria(str(item[idx])),
            reverse=rev,
        )
    )
    return found


SORT_PATTERN = [
    "((?P<parent>[^/]+)/)?(?P<basename>[^/]+)$",
]


def find_data_files(folders, includes, **ctx):
    # includes = [include] if include else env.includes
    # sort_pattern = [
    #     "((?P<parent>[^/]+)/)?(?P<basename>[^/]+)$",
    # ]
    found = find_files(
        folders,
        includes=includes,
        sort_by="keys",
        sort_pattern=SORT_PATTERN,
        **ctx,
    )

    return found
