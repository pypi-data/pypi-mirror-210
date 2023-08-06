# -*- coding: utf-8 -*-
"""This module contains basic methods and definitions that would be used
by other `gutools` modules.
"""

import sys
import os
import types
import asyncio
import hashlib
import locale
import uuid
import random
import inspect
import types
import fnmatch
import re
import yaml
import time
import stat
import dateutil.parser as parser
from dateutil.relativedelta import relativedelta

# import itertools
from dateutil import tz

from datetime import datetime
from codenamize import codenamize
from urllib import parse
from io import StringIO

# from functools import partial
from collections import deque
from collections.abc import Iterable
from weakref import WeakValueDictionary, WeakSet
from .colors import *
from pprint import pformat

import arrow
import numpy as np

TZ = tz.gettz("Europe/Madrid")


def sitems(d, exclude=None):
    exclude = exclude or []
    keys = list(d)
    keys.sort()
    for k in keys:
        for pattern in exclude:
            if re.match(pattern, k):
                break
        else:
            yield k, d[k]


def soft(q, **kw):
    for k, v in kw.items():
        _v = q.get(k)
        if _v is None or (isinstance(_v, float) and np.isnan(_v)):
            q[k] = v
    return q


def xoft(q, **kw):
    for k, v in kw.items():
        _v = q.get(k)
        if (
            not _v
            and (
                isinstance(
                    _v,
                    (
                        types.NoneType,
                        int,
                        float,
                        str,
                        tuple,
                        list,
                        dict,
                        set,
                    ),
                )
            )
            or (isinstance(_v, float) and np.isnan(_v))
        ):
            q[k] = v
    return q


def dsoft(q, kw, extend=False):
    for k, v in kw.items():
        _v = q.get(k)
        if _v is None or (isinstance(_v, float) and np.isnan(_v)):
            q[k] = v
        elif extend:
            # create a new column with pattern
            pattern = f"{k}\.(\d+)"
            n = 0
            for key in q:
                m = re.match(pattern, key)
                if m:
                    n = max(n, int(m.group(1)))
            n += 1
            k = f"{k}.{n}"
            q[k] = v

    return q


def csoft(q, **kw):
    q = q.__class__(q)
    for k, v in kw.items():
        if q.get(k, None) is None:
            q[k] = v
    return q


def chard(q, **kw):
    q = q.__class__(q)
    q.update(kw)
    return q


def supdate(container, data):
    for k, v in data.items():
        holder = container.setdefault(k, dict())
        soft(holder, **v)
    return container


# -------------------------------------------------------
#  hashing
# -------------------------------------------------------
def hash_point(anything):
    h = hashlib.sha1(str(anything).encode("utf-8"))
    return int(h.hexdigest(), 16)


def get_blueprint(data, keys):
    if not isinstance(keys, set):
        keys = set(keys)
    blue = {k: data[k] for k in keys.intersection(data)}
    sign = hash_point(blue)
    return sign


# -----------------------------------------------------------
# Find sub-classes
# -----------------------------------------------------------
def get_subclasses(klass):
    used = set()
    found = set()

    FORBIDEN = set(
        [
            r"pandas",
        ]
    )

    pending = set()
    for string in sys.modules:
        for pattern in FORBIDEN:
            if re.match(pattern, string):
                break
        else:
            pending.add(string)

    while pending:
        for mname in pending:
            module = sys.modules[mname]
            used.add(mname)

            for name in dir(module):
                try:
                    obj = getattr(module, name)
                    if inspect.isclass(obj) and issubclass(obj, klass):
                        found.add(obj)
                except FutureWarning as why:
                    foo = 1
                except Exception as why:
                    foo = 1
                    pass

        # check is any new module has been loaded during inspection
        pending = used.symmetric_difference(sys.modules)
    return found


# -------------------------------------------------------
#  asyncio nested loops
# -------------------------------------------------------
# import nest_asyncio
# nest_asyncio.apply()

# -----------------------------------------------------------
# Misc converters handling
# -----------------------------------------------------------


def Str(item):
    "Extended String converter"
    if isinstance(item, bytes):
        return item.decode("UTF-8")
    return str(item)


def Float(item):
    "Extended Float converter"
    return float(item or 0)


def Int(item):
    "Extended Int converter. Valid is number can be converted to INT without loosing precission"
    f = float(item or 0)
    i = int(f)
    if i == f:
        return i
    raise ValueError()


def Date(item, tz=TZ):
    return parser.parse(item, ignoretz=True)


# -----------------------------------------------------------
# Containers
# -----------------------------------------------------------


# -----------------------------------------------------------
# URI handling
# -----------------------------------------------------------
reg_uri = re.compile(
    """(?imsx)
    (?P<fservice>
        (
            (?P<fscheme>
                (?P<direction>[<|>])?(?P<scheme>[^:/]*))
                ://
        )?
        (?P<xhost>
           (
                (?P<auth>
                   (?P<user>[^:@/]*?)
                   (:(?P<password>[^@/]*?))?
                )
            @)?
           (?P<host>[^@:/?]*)
           (:(?P<port>\d+))?
        )
    )?
    (?P<path>/[^?]*)?
    (\?(?P<query>[^#]*))?
    (\#(?P<fragment>.*))?
    """
)

# https://stackoverflow.com/questions/14693701/how-can-i-remove-the-ansi-escape-sequences-from-a-string-in-python
# 7-bit C1 ANSI sequences
ansi_escape = re.compile(
    r"""
    \x1B  # ESC
    (?:   # 7-bit C1 Fe (except CSI)
        [@-Z\\-_]
    |     # or [ for CSI, followed by a control sequence
        \[
        [0-?]*  # Parameter bytes
        [ -/]*  # Intermediate bytes
        [@-~]   # Final byte
    )
""",
    re.VERBOSE,
)

# 7-bit and 8-bit C1 ANSI sequences
ansi_escape_8bit = re.compile(
    rb"""
    (?: # either 7-bit C1, two bytes, ESC Fe (omitting CSI)
        \x1B
        [@-Z\\-_]
    |   # or a single 8-bit byte Fe (omitting CSI)
        [\x80-\x9A\x9C-\x9F]
    |   # or CSI + control codes
        (?: # 7-bit CSI, ESC [
            \x1B\[
        |   # 8-bit CSI, 9B
            \x9B
        )
        [0-?]*  # Parameter bytes
        [ -/]*  # Intermediate bytes
        [@-~]   # Final byte
    )
""",
    re.VERBOSE,
)

# Example: result = ansi_escape_8bit.sub(b'', somebytesvalue)


def normalize_key(key):
    return key.strip().lower().replace(" ", "_")


def basename_key(key):
    return key.split(".")[-1]


def parse_uri(uri, bind=None, drop_nones=False, **kw):
    """Extended version for parsing uris:

    Return includes:

    - *query_*: dict with all query parameters splited

    If `bind` is passed, *localhost* will be replace by argument.

    """

    m = reg_uri.match(uri)
    if m:
        for k, v in m.groupdict().items():
            if k not in kw or v is not None:
                kw[k] = v
        if bind:
            kw["host"] = kw["host"].replace("localhost", bind)
        if kw["port"]:
            kw["port"] = int(kw["port"])
            kw["address"] = tuple([kw["host"], kw["port"]])
        if kw["query"]:
            kw["query_"] = dict(parse.parse_qsl(kw["query"]))

        kw['uri'] = uri

    if drop_nones:
        kw = {k: v for k, v in kw.items() if v is not None}
    return kw


def build_uri(
    fscheme="",
    direction="",
    scheme="",
    xhost="",
    host="",
    port="",
    path="",
    query="",
    fragment="",
    query_={},
    **kw,
):
    """Generate a URI based on individual parameters"""
    uri = ""
    if fscheme:
        uri += fscheme or ""
    else:
        if not direction:
            uri += scheme or ""
        else:
            uri += f"{direction}{scheme or ''}"
    if uri:
        uri += "://"

    if xhost:
        uri += xhost
    else:
        host = host or f"{uuid.getnode():x}"
        uri += host
        if port:
            uri += f":{port}"

    if path:
        uri += f"{path}"

    if query_:
        # query_ overrides query if both are provided
        query = "&".join([f"{k}={v}" for k, v in query_.items()])

    elif isinstance(query, dict):
        query = "&".join([f"{k}={v}" for k, v in query.items()])

    if query:
        uri += f"?{query}"
    if fragment:
        uri += f"#{fragment}"

    return uri


def expandpath(path):
    if path:
        path = os.path.expanduser(path)
        path = os.path.expandvars(path)
        path = os.path.abspath(path)
        while path[-1] == "/":
            path = path[:-1]
    return path


def zip_like(master, other=None):
    """Smart iterator to handle with diferent types of container or singke values."""
    if not isinstance(master, (list, tuple, set, dict)):
        master = [master]

    if other is None:
        other = master
    elif not isinstance(other, (list, tuple, set, dict)):
        other = [other]

    if isinstance(master, dict):
        assert isinstance(other, dict)
        for k, v in master.items():
            if k in other:
                yield k, v, other[k]
    else:  # TODO: coding 'other' being an generator
        L = len(other)
        assert master.__class__ == other.__class__
        for k, v in enumerate(master):
            if k < L:
                yield k, v, other[k]


def zip_items_like(master, other):
    """Smart iterator to handle with diferent types of container or singke values."""
    if not isinstance(master, (list, tuple, set, dict)):
        master = [master]
    if not isinstance(other, (list, tuple, set, dict)):
        other = [other]

    if isinstance(master, dict):
        assert isinstance(other, dict)
        for k, v in master.items():
            if k in other:
                yield k, v, other[k]
    else:  # TODO: coding 'other' being an generator
        L = len(other)
        assert master.__class__ == other.__class__
        for k, v in enumerate(master):
            if k < L:
                yield k, v, other[k]


# --------------------------------------------------
# General Helpers
# --------------------------------------------------
def _signature(req):
    raw = bytes(str(req), "utf-8")
    return hashlib.md5(raw).hexdigest()


def f2s(value: float) -> str:
    """Print a float removing all right zeros and colon when possible."""
    return ("%.15f" % value).rstrip("0").rstrip(".")


def expanddict(pattern, **ctx):
    value = pattern.format_map(ctx)
    return value


def relpath(root, path):
    parts = root.split(path)[-1].split("/")
    parts = [p for p in parts if p]
    return "/".join(parts)


def expand_uri(uri):
    if isinstance(uri, str):
        uri = parse_uri(uri)
    uri["path"] = expandpath(uri["path"])

    return build_uri(**uri)


def combine_uris(root, child, extend={"path": True}, build=True):
    if isinstance(root, str):
        root = parse_uri(root)
    else:
        root = dict(root)
    if isinstance(child, str):
        child = parse_uri(child)

    for key, value in child.items():
        if extend.get(key):
            value = f"{root.get(key) or ''}{value}"
        if value:
            root[key] = value

    if build:
        root = build_uri(**root)
    return root


def replace_uri(uri, klass=None, **fields):
    kw = parse_uri(uri)
    if klass:
        fields["fscheme"] = snake_case(klass.__name__, separator="-")
    kw.update(fields)
    return build_uri(**kw)


def get_self_uri(item, **defaults):
    """Try to create a fingerprint of item using all basic
    types that represent the item at this point.
    """
    fingerprint = {
        k: v
        for (k, v) in flatdict(item.__dict__).items()
        if isinstance(v, BASIC_TYPES_EXT)
    }

    klass = snake_case(item.__class__.__name__, separator="-")
    fingerprint["__class__"] = klass
    fingerprint = "|".join([str(i) for i in fingerprint.items()])
    path = f"/{codenamize(fingerprint, join='_', hash_algo='sha1')}"

    defaults.setdefault("scheme", klass.lower())
    defaults.setdefault("host", f"{uuid.getnode():x}")
    defaults.setdefault("path", path)

    uri = build_uri(**defaults)
    return uri


# --------------------------------------------------------------------
# utasks
# --------------------------------------------------------------------
class utask_queue(deque):
    def __iter__(self):
        return self

    def __next__(self):
        if len(self) == 0:
            raise StopIteration()
        task = self.popleft()
        restart = True
        try:
            for item in task:
                return item
            restart = task._restart
        except Exception as why:
            print(why)
        finally:
            if restart:
                self.append(task)


class uTask:
    __slots__ = "gen", "func", "args", "kw", "_restart"

    def __init__(self, func, *args, **kw):
        self.gen = None
        self._restart = kw.pop("__restart__", True)
        self.func = func
        self.args = args
        self.kw = kw
        self.restart()

    def __str__(self):
        return f"{self.func.__name__}({self.args}, {self.kw})"

    def __repr__(self):
        return str(self)

    def __iter__(self):
        return self

    def __next__(self):
        for item in self.gen:
            return item
        else:
            if self._restart:
                self.restart()
            raise StopIteration()

    def restart(self):
        self.gen = self.func(*self.args, **self.kw)


class NOP:
    """No Operation"""


# --------------------------------------------------------------------
# iterators helpers
# --------------------------------------------------------------------


def best_score(container, reverse=False):
    score = min(container.values()) if reverse else max(container.values())
    for k, v in container.items():
        if v == score:
            return k
    raise RuntimeError("someone has modified container somehow...")


# containers


def dset(d, key, value, *args, **kw):
    if key not in d:
        if args or kw:
            value = value(*args, **kw)
        d[key] = value
    return d[key]


# next_lid = random.randint(-10**5, 10**5)
next_lid = random.randint(0, 10**5)


def new_uid():
    global next_lid
    next_lid += 1
    return next_lid  # TODO: remove, just debuging
    # return uidfrom(next_lid)


def uidfrom(lid):
    if not lid:
        return lid

    lid = str(lid)
    lid = bytes(lid, encoding="UTF-8")

    algo = "md5"
    assert algo in hashlib.algorithms_guaranteed
    h = hashlib.new(algo)
    h.update(lid)
    uid = h.hexdigest()

    return uid


# --------------------------------------------------------------------
# containers helpers
# --------------------------------------------------------------------


def try_convert(container, klasses=[int]):
    if not isinstance(klasses, list):
        klasses = [klasses]

    for k, v in list(container.items()):
        for f in klasses:
            try:
                container[k] = f(v)
                break
            except Exception as why:
                continue
    return container


class wset(WeakSet):
    def __str__(self):
        return f"|{pformat(list(self))[1:-1]}|"

    def __repr__(self):
        return self.__str__()


def WKD(iterator):
    "Build a WeakKeyDictionary from object or object iterators"
    if isinstance(iterator, wset):
        return iterator

    if not hasattr(iterator, "__len__"):
        if iterator:
            iterator = [iterator]
        else:
            iterator = []
    return wset({k: True for k in iterator})


# https://stackoverflow.com/questions/6760685/creating-a-singleton-in-python
class Singleton(type):
    _instances = {}
    _callargs = {}

    def __call__(cls, *args, **kwargs):
        if cls in cls._instances:
            if args or kwargs and cls._callargs[cls] != (args, kwargs):
                warn = """
WARNING: Singleton {} called with different args\n
  1st: {}
  now: {}
""".format(
                    cls, cls._callargs[cls], (args, kwargs)
                )
                print(warn)
        else:
            cls._instances[cls] = super(Singleton, cls).__call__(
                *args, **kwargs
            )
            cls._callargs[cls] = (args, kwargs)
        return cls._instances[cls]


# #Python2
# class MyClass(BaseClass):
# __metaclass__ = Singleton

# #Python3
# class MyClass(BaseClass, metaclass=Singleton):
# pass


class Xingleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        __call__ = super(Xingleton, cls).__call__
        __init__ = cls.__init__
        args2 = prepare_call_args(__init__, *args, **kwargs)
        # args2 = args

        existing = cls._instances.get(cls)  # don't use setdefault here
        if existing is None:
            existing = cls._instances[cls] = WeakValueDictionary()

        instance = existing.get(args2)
        if instance is None:
            instance = existing[args2] = __call__(*args2)
        return instance


# ---------------------------------------------------------------------
# A Dynamic Programming based Python program for edit distance problem
# ---------------------------------------------------------------------


def retry(delay=0.1):
    """Retray the same call where the funcion is invokerd but
    a few instant later"""
    frame = inspect.currentframe().f_back
    calling_args = frame.f_code.co_varnames[: frame.f_code.co_argcount]
    calling_args = [frame.f_locals[k] for k in calling_args]
    func = get_calling_function(2)
    if isinstance(func, types.MethodType):
        calling_args.pop(0)

    loop = asyncio.get_event_loop()
    loop.call_later(0.2, func, *calling_args)

    foo = 1


async def add_to_loop(*aws, delay=0.1, loop=None):
    for coro in aws:
        asyncio.ensure_future(coro, loop=loop)
        await asyncio.sleep(delay, loop=loop)


# --------------------------------------------------
# RegExp operations
# --------------------------------------------------


def exp_compile(pattern):
    try:
        exp = re.compile(pattern, re.DOTALL)
        # if regexp has no groups, I assume is a wildcard
        if not exp.groups:
            raise re.error("force wildcard")
    except re.error:
        try:
            exp = fnmatch.translate(pattern)
            exp = re.compile(exp, re.DOTALL)
        except re.error:
            exp = re.compile(".*")

    return exp


def _prepare_test_regext(regexp=None, wildcard=None, test=None):
    test = test or list()

    if isinstance(regexp, (list, tuple, set)):
        test.extend(regexp)
    else:
        test.append(regexp)

    if not isinstance(wildcard, (list, tuple)):
        wildcard = [wildcard]
    for wc in wildcard:
        if wc and isinstance(wc, str):
            wc = fnmatch.translate(wc)
            test.append(wc)

    test = [re.compile(m).search for m in test if m]

    return test  # you can compile a compiled expression


def _find_match(string, test):
    b_m, b_d = None, {}
    for reg in test:
        if isinstance(reg, types.BuiltinFunctionType):
            m = reg(string)
        else:
            m = reg.search(string)
        if m:
            candidate = m.groupdict()
            if len(candidate) > len(b_d):
                b_m, b_d = m, candidate
            if not candidate and not b_d:
                # print(f"warning: string match but no groups are defined.")
                b_m = m

    return b_m

    # if test:
    # for match in test:
    # m = match(string)
    # if m:
    # return m


def _return_matched_info(m, info):
    if info in ("d", "s"):
        return m.groupdict()
    elif info == "g":
        return m.groups()
    return m.group(0)


def _return_unmatched(info):
    if info in ("d", "s"):
        return dict()
    elif info == "g":
        return list()


def parse_string(string, regexp=None, wildcard=None, info=None):
    test = _prepare_test_regext(regexp, wildcard)
    m = _find_match(string, test)
    if m:
        return _return_matched_info(m, info)
    return _return_unmatched(
        info
    )  # to return cpmpatible values in upper stack


def parse_date(date):
    if isinstance(date, str):
        return parser.parse(date)
    return date


def parse_date_x(date):
    if isinstance(date, str):
        date = date.replace("/", "-")
        safe_loc = locale.getlocale()
        try:
            date = arrow.get(date)._datetime
        except Exception:
            for loc in (
                "en_US.UTF-8",
                "es_ES.UTF-8",
            ):
                locale.setlocale(locale.LC_ALL, loc)
                for fmt in ["%d-%m-%Y", "%d-%b-%Y"]:
                    try:
                        date = datetime.strptime(date, fmt)
                        return date
                    except:
                        pass
                else:
                    pass
        finally:
            locale.setlocale(locale.LC_ALL, safe_loc)

    return date


def parse_relativedelta(item):
    units = {
        "s": "seconds",
        "m": "minutes",
        "h": "hours",
        "d": "days",
    }

    m = re.match(r"(?P<value>\d+)\w*(?P<unit>.+)$", item.lower(), re.DOTALL)
    d = m.groupdict()
    kw = {units[d["unit"]]: float(d["value"])}
    return relativedelta(**kw)


# --------------------------------------------------
# File perations
# --------------------------------------------------


def direct_lines(file, begin_payload=None):
    "Just simple a wrapper to be able to call file.tell()"
    if begin_payload is not None:
        file.seek(begin_payload, os.SEEK_SET)

    line = file.readline()
    while line:
        yield line
        line = file.readline()


def sorted_lines(file):
    "Just simple a wrapper to be able to call file.tell() and yields lines sorted"
    lines = dict()
    for line in direct_lines(file):
        key = line.split(",")[0]
        lines[key] = line, file.tell()

    # sort lines by 1st key
    keys = list(lines.keys())
    keys.sort()

    for k in keys:
        line, pos = lines.pop(k)
        # move file cursor for extenal progress
        file.seek(pos, os.SEEK_SET)
        yield line


def reversed_lines(file):
    "Generate the lines of file in reverse order."
    part = ""
    for block in reversed_blocks(file, end_payload, blocksize):
        for c in reversed(block):
            if c == "\n" and part:
                yield part[::-1]
                part = ""
            part += c
    if part:
        yield part[::-1]


def reversed_blocks(
    file,
    end_payload=0,
    blocksize=4096,
):
    "Generate blocks of file's contents in reverse order."
    file.seek(0, os.SEEK_END)
    here = file.tell()
    while end_payload < here:
        delta = min(blocksize, here)
        here -= delta
        file.seek(here, os.SEEK_SET)
        yield file.read(delta)


def fileiter(
    top,
    regexp=None,
    wildcard=None,
    info="d",
    relative=False,
    exclude=None,
    neg_reg=None,
    stats=False,
):
    """Iterate over files
    info == 'd'   : returns filename, regexp.groupdict()
    info == 's'   : same, but including mtime and file size
    info == 'g'   : returns filename, regexp.groups()
    info == None: : returns filename

    Allow single expressions or iterator as regexp or wildcard params
    """
    neg_reg = _prepare_test_regext(neg_reg, None)

    include = _prepare_test_regext(regexp, wildcard)
    exclude = _prepare_test_regext(exclude, None)

    if neg_reg and not include:
        include = _prepare_test_regext(".*", None)

    for root, _, files in os.walk(top):
        for name in files:
            filename = os.path.join(root, name)
            if os.path.sep != "/":
                filename = filename.replace(os.path.sep, "/")
            # print(filename)
            if info in ("s",):
                try:
                    st = os.stat(filename)
                except:
                    continue
                stats = {
                    "mtime": st.st_mtime,
                    "size": st.st_size,
                    "blocks": st.st_blocks,
                }
            else:
                stats = {}

            if relative:
                filename = filename.split(top)[-1][1:]

            m3 = _find_match(filename, exclude)
            if m3:
                continue

            m4 = _find_match(filename, neg_reg)
            if m4:
                continue

            m1 = _find_match(filename, include)
            m2 = _find_match(filename, exclude)

            if m1 and not m2:
                m1 = _return_matched_info(m1, info)
                if m1 is not None:
                    m1.update(stats)
                    yield filename, m1
                else:
                    yield filename
            elif m2 and not m1:
                m2 = _return_matched_info(m2, info)
                if m2 is not None:
                    m2.update(stats)
                    yield filename, m2
                else:
                    yield filename

    foo = 1


def get_calling_function(level=1, skip_modules=None):
    """finds the calling function in many decent cases."""
    # stack = inspect.stack(context)
    # fr = sys._getframe(level)   # inspect.stack()[1][0]
    skip_modules = set(skip_modules or [])
    stack = inspect.stack()
    while level < len(stack):
        fr = stack[level][0]
        co = fr.f_code
        for i, get in enumerate(
            [
                lambda: fr.f_globals[co.co_name],
                lambda: getattr(fr.f_locals["self"], co.co_name),
                lambda: getattr(fr.f_locals["cls"], co.co_name),
                lambda: fr.f_back.f_locals[co.co_name],  # nested
                lambda: fr.f_back.f_locals["func"],  # decorators
                lambda: fr.f_back.f_locals["meth"],
                lambda: fr.f_back.f_locals["f"],
            ]
        ):
            try:
                func = get()
            except (KeyError, AttributeError):
                pass
            else:
                if hasattr(func, "__code__") and func.__code__ == co:
                    if func.__module__ not in skip_modules:
                        return func
        level += 1
    raise AttributeError("func not found")


def copyfile(src, dest, override=False):
    if os.path.exists(dest) and not override:
        return

    folder = os.path.dirname(dest)
    if not os.path.exists(folder):
        os.makedirs(folder)
    with open(src, "rb") as s:
        with open(dest, "wb") as d:
            d.write(s.read())

    st = os.stat(src)
    os.chmod(dest, stat.S_IMODE(st.st_mode))


# ----------------------------------
# Container Operations
# ----------------------------------

TYPES = []
for k in types.__all__:
    klass = getattr(types, k)
    try:
        if isinstance(TYPES, klass):
            pass
        TYPES.append(klass)
    except Exception as why:
        pass
TYPES = tuple(TYPES)


def update_context(context, *args, **kw):
    """Update several data into a *holder* context.
    args can be anything that we can obain a *dict* alike object.
    """
    __avoid_nulls__ = kw.pop("__avoid_nulls__", True)

    if __avoid_nulls__:
        for k, v in kw.items():
            if v is not None:
                context[k] = v
    else:
        context.update(kw)

    for item in args:
        if isinstance(item, dict):
            d = item
        elif hasattr(item, "as_dict"):
            d = item.as_dict()
        elif hasattr(item, "__dict__"):
            d = item.__dict__
        elif hasattr(item, "__getstate__"):
            d = item.__getstate__()
        else:
            d = dict()
            for k in dir(item):
                if k.startswith("_"):
                    continue
                v = getattr(item, k)
                if v.__class__.__name__ == "type" or isinstance(
                    v, TYPES
                ):  # (types.FunctionType, types.MethodType, types.MethodWrapperType, types.BuiltinFunctionType)):
                    continue
                d[k] = v

        if __avoid_nulls__:
            for k, v in d.items():
                if v is not None:
                    context[k] = v
        else:
            context.update(d)


def convert_container(item, *klasses):
    """Try to convert a text into more fine grain object:

    when klass is provided, tries as much to convert to klass

    - list
    - dict
    - boolean
    - integer
    - etc

    # TODO: improve with regexp and dict of candidates.
    """
    klasses = list(klasses)
    while klasses:
        klass = klasses.pop(0)
        if isinstance(klass, (list, tuple)):
            klasses = [k for k in klass] + klasses
            continue

        if klass in (list,):
            item = [
                convert_container(t.strip(), *klasses)
                for t in item.split(",")
            ]

        if klass in (dict,):
            item = [
                convert_container(t.strip(), *klasses)
                for t in item.split(",")
            ]

        if klass:
            item = klass(item)

    return item


# def load_config(path, **kw):
# loader = {
#'yaml': [yaml.load, {'Loader': yaml.FullLoader,}],
#'json': [json.load, {}],
#'conf': [parse_config_file, {}],
# }
# config = dict()
# path = expandpath(path)
# if path and os.path.exists(path):
# ext = os.path.splitext(path)[-1][1:]
# if ext not in loader:
# ext = 'yaml'
# loader, kwargs = loader[ext]
# kwargs = dict(kwargs)
# kwargs.update(kw)
# with open(path, 'r') as f:
# config = loader(f, **kwargs) or config
# return config


# def file_lookup(pattern, path=None):
# """Search for files in several folders using a strategy lookup.
# - pattern: relative or abspath
# - srcfile: file or directory where to look for last
# """
# root, name = os.path.split(pattern)
# if root:
# pattern = expandpath(pattern)

# if os.path.isabs(pattern):
# candidates, pattern = os.path.split(pattern)
# candidates = [candidates]
# else:
# if not isinstance(path, list):
# path = [path]

# candidates = []
# for p in path:
# p = p or '.'
# for c in  ['/etc', os.path.dirname(__file__),'~/.config', '~', '.', p]:
# if c not in candidates:
# candidates.append(c)  # don't use set to preserve order

## expand all parents for each candidate
##print(f">>> candidates={candidates}")
# folders = []
# for path in candidates:
# head = tail = expandpath(path)
# ascend = list()
# while tail:
# ascend.append(head)
# head, tail = os.path.split(head)

# ascend.reverse()
## add only new ones (is faster here that check twice later)
# for path in ascend:
# if path not in folders:
# folders.append(path)

# conf = dict()
# for root in folders:
# path = os.path.join(root, pattern)
# path = os.path.expanduser(path)
# path = os.path.expandvars(path)
# if not os.path.exists(path):
##print(f"?  {path}? - no")
# continue
##print(f"> {path}? - yes")
# yield path


# def merge_config(pattern, srcfile=None):
# """Merge config files using the same lookup pattern"""
# conf = dict()
# for path in file_lookup(pattern, srcfile):
# print(f"- loading: {path}")
# c = load_config(path)
##c = yaml.load(open(path), Loader=yaml.FullLoader)
# if not c:
# continue
## merge with existing values
## for name in c.get('loggers', {}):
## print(f" - {name}")
## foo = 1
# for section, values in c.items():
# if isinstance(values, dict):
# org = conf.setdefault(section, dict())
# org.update(values)
# else:
# conf[section] = values
# return conf


# def save_config(config, srcfile):
# srcfile = expandpath(srcfile)
# root, path = os.path.split(srcfile)
# os.makedirs(root, exist_ok=True)

# yaml.dump(config, open(srcfile, 'w'), default_flow_style=False)


def basic_type(item):
    if isinstance(
        item,
        (
            bool,
            int,
            float,
            str,
            bytes,
        ),
    ):
        return True
    return False


def get_serializable_state(config):
    state = dict()
    for k, v in flatdict(config).items():
        if basic_type(item):
            state[k] = v

    return state


# def save_config(config, path):
# raise DeprecationWarning()

# saver = {
# 'yaml': partial(yaml.dump, default_flow_style=False),
# 'json': json.dump,
# }
# ext = os.path.splitext(path)[-1][1:]
# saver = saver.get(ext, saver['yaml'])
# with open(path, 'w') as f:
# config = saver(config, f)


def yaml_decode(raw: str):
    fd = StringIO(raw)
    return yaml.load(fd)


def yaml_encode(item: str):
    fd = StringIO()
    yaml.dump(item, fd, default_flow_style=False)
    return fd.getvalue()


def identity(item):
    "convenience function"
    return item


def dropfrom(cont, attr, value, recursive=True):
    for key in list(cont.keys()):
        print(f"key: {key}")
        if key == ("202005", "diary", "20200521", "atlas", "core"):
            foo = 1
        item = cont[key]
        if attr in item:
            if item[attr] == value:
                cont.pop(key)
                return
            continue

        if hasattr(item, "keys"):
            print(f">> in : {key}")
            dropfrom(item, attr, value, recursive)
            print(f"<< out: {key}")


def change_monitor(paths, timeout=None, delay=1):
    timestamp = dict()
    t0 = time.time()

    while True:
        for path in list(paths):
            t1 = os.stat(path).st_mtime
            t2 = timestamp.setdefault(path, t1)
            if t2 < t1:
                yield path
                timestamp[path] = t1
        else:
            time.sleep(delay)
            t1 = time.time()
            if timeout and t1 - t0 > timeout:
                break


# --------------------------------------------------
# Debugger/Testing
# --------------------------------------------------
def void():
    pass


class Record(dict):
    """Specific subclass dictorionary that:
    - remember keys order when someone has used before (in order)
    - iterate dict with this order
    """

    ORDER = list()
    USED = list()

    @classmethod
    def set_order(cls, order):
        assert isinstance(order, list)
        cls.ORDER = order

    def __init__(self, *args, **kw):
        self["time"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")
        super().__init__(*args, **kw)

    def __setitem__(self, key, value):
        if isinstance(value, type(None)):
            value = str(value)

        if key not in self.USED and key not in self.ORDER:
            self.USED.append(key)

        super().__setitem__(key, value)

    def reset(self):
        for k in set(self.ORDER).intersection(self.keys()):
            self.pop(k)
        for k in self.keys():
            self[k] = ""
        self["time"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")

    def items(self):
        keys = list(self.keys())
        for key in self.ORDER:
            if key in self:
                yield key, self[key]
                keys.remove(key)

        for key in self.USED:
            if key in self:
                yield key, self[key]


class Dumper:
    def __init__(self, out):
        self.out = out
        self.flush = getattr(self.out, "flush", void)
        self.sep = "|"

        self._template_format = {
            r"time": r"{time:>{size}}",
            r"event": r"{event:>25}",
            # r'(name\d+)': r'{\1:{size}}',
            r"(name\d+)": r"{\1:25}",
        }
        self._format = dict()

    def write(self, record):
        record["time"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")
        indent = ""
        for line in self.format(record).split("\n"):
            self.out.write(f"{indent}{line}\n")
            indent = " ... "
        self.flush()

    def format(self, record):
        fields = []
        if "event" in record:
            record["event"] = "# {event}".format(**record)
        for k, v in record.items():
            fmt = self._get_fmt(k, v)
            fields.append(fmt)

        fields.append("")
        fmt = self.sep.join(fields)
        return fmt.format(**record)

    def _get_fmt(self, key, value):
        fmt = self._format.get(key)
        if not fmt:
            size = str(2 + len(str(value)))
            for pattern, exp in self._template_format.items():
                if re.search(pattern, key):
                    fmt = self._format[key] = re.sub(
                        pattern, exp, key
                    ).replace(
                        "{size}", size
                    )  # you can extend replacemente chain
                    break
            else:
                fmt = f"{value:^25}"
                # raise RuntimeError(f"unable fo find a format for {key} : {value}")
        return fmt


# find module
def find_classes_iter(baseclass=None, regexp="(?!x)x"):
    reg = re.compile(regexp, re.DOTALL)
    for module in sys.modules.values():
        for name in dir(module):
            if not reg.match(name):
                continue
            obj = getattr(module, name)
            if not (baseclass and issubclass(obj, baseclass)):
                continue
            yield obj


def find_classes(baseclass=None, regexp="(?!x)x"):
    return [x for x in find_classes_iter(baseclass, regexp)]


def find_by_regexp(source, key, default_key="<default>"):
    """Find a value searching keys by regexp.
    If not found a default key will be used.

    Note: returns the longest candidate.
    """
    b_key, b_value = None, None
    for regexp, value in source.items():
        m = re.match(regexp, key)
        if m:
            match = m.group(0)
            if not b_key or len(match) > len(b_key):
                b_key, b_value = match, value

    if b_key:
        return b_value
    return source.get(default_key)


# - End -


# -----------------------------------------------------------
# config files
# -----------------------------------------------------------

"""
Helpers for loading, saving, merging, expand and condense config files.
"""

import os
import sys
import yaml
import inspect
from colorama import Fore


# TODO : review


def guess_configfile_name(level=2):
    """Guess a config file name based on the calling module to the function

    Example:

    Calling from a function in 'atlas.controllers.historical' module
    it yields:

    '~/.config/atlas/historical.yaml'

    """
    func = get_calling_function(level=level)
    mod = func.__func__.__module__
    if mod:
        mod = mod.split(".")
        if len(mod) > 1:
            return f"~/.config/{mod[0]}/{mod[-1]}.yaml"

        return f"~/.config/{mod[0]}.yaml"


def get_config(default, create=True, level=3):
    configfile = guess_configfile_name(level)

    config = merge_config(configfile)
    if not config and create:
        # apply default_config
        config = save_config(default, configfile, condense=True)
    config = expand_config(config)
    return config


def file_lookup(pattern, path, appname=""):
    """Search for files in several folders using a strategy lookup.
    - pattern: relative or abspath
    - path: file or directory where to look until if reac
    """
    debug = os.environ.get("DEBUG", False)

    root, name = os.path.split(pattern)
    if root:
        pattern = expandpath(pattern)

    path = path or "."
    if os.path.isabs(pattern):
        candidates, pattern = os.path.split(pattern)
        candidates = [candidates]
    else:
        candidates = [f"/etc/{appname}"]
        stack = inspect.stack()
        while stack:
            dirname = os.path.dirname(stack.pop(0)[0].f_code.co_filename)
            if dirname and dirname not in candidates:
                candidates.append(dirname)

        candidates.extend(
            [
                os.path.dirname(__file__),
                f"~/.config/{appname}",
                f"~/{appname}",
                path,
                ".",
            ]
        )
        debug and print(f"CAND: {candidates}")

    # expand all parents for each candidate
    folders = []
    for path in candidates:
        head = tail = expandpath(path)
        ascend = list()
        while tail:
            ascend.append(head)
            head, tail = os.path.split(head)

        ascend.reverse()
        # add only new ones (is faster here that check twice later)
        for path in ascend:
            if path not in folders:
                debug and print(f"+ {path}")
                folders.append(path)

    debug and print(f"FOLD: {folders}")
    for root in folders:
        path = os.path.join(root, pattern)
        path = os.path.expanduser(path)
        path = os.path.expandvars(path)
        if not os.path.exists(path):
            # debug and print(f"not exist:  {path}? - no")
            continue
        debug and print(f"> exists: {path}? - yes")
        yield path


# --------------------------------------------------
# RegExp
# --------------------------------------------------
def multi_match(regexps, string):
    for pattern in regexps:
        m = re.match(pattern, string)
        if m:
            return m.groupdict()
