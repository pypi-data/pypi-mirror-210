"""
Shell:

- [x] Shell is configured with command pattern and specific response regexp capturing.
- [x] Use jinja2 for as pattern template instead string.format_map
- [-] load templates and responses from yaml file (optional) --> Not Practial

Handler:

- [x] use state md5 as key for { state : callback } map
- [ ] allow multiples handlers for searching callbacks.

Daemon:

- [x] use asyncio / curio for handling multiple agents.
- [ ] define daemon interface as extensible pattern.
- [ ] load plugins as threads/async loops
- [ ] hot plugin reloading

"""
import re
from subprocess import Popen, PIPE, STDOUT
import sys
import os
import time
from datetime import datetime
import getpass
import hashlib
import yaml
import random
import platform
import inspect
import shutil
import itertools

import asyncio, asyncssh, sys
from asyncssh.connection import SSHClientConnectionOptions

from asyncio import run, wait, create_task, sleep, FIRST_COMPLETED, Queue


from jinja2 import Environment, BaseLoader, FileSystemLoader

from glom import glom, assign, T
from glom.core import TType

# import jmespath

# import wingdbstub

# import curio
# from pycelium.shell import STM

from .tools.calls import scall
from .tools.colors import *
from .tools.logs import logger

from .definitions import (
    ANY_CATEGORY,
    DEFAULT_CONNECTION,
    DEFAULT_EXECUTOR,
    ENV,
    RUN,
)

# from containers import walk, rebuild, merge, new_container
from .tools.containers import (
    walk,
    rebuild,
    merge,
    amerge,
    new_container,
    xoverlap,
    tspec,
    bspec,
    search,
    gather_values,
    option_match,
)
from .tools.metrics import likelyhood6

log = logger(__name__)
trace = logger(f'{__name__}.trace')


# ------------------------------------------------
# Helpers
# ------------------------------------------------


def temp_filename():
    return f'/tmp/{time.time()}.{random.randint(0, 10**9)}.delete_me'


def update(root, spec, new, mode="add", **kw):
    holder = glom(root, spec, default={})
    new = merge(holder, new, mode=mode, **kw)

    if spec:
        return assign(root, spec, new, missing=dict)
    else:
        root.update(new)

    return new


def jinja2params(template):
    """TODO:

    extract more complex expressions:

    nice {{ 'sudo' if sudo else '' }}  pip3 list {{ '--outdated' if upgradable else ' }}'



    """
    pattern = r'\{\{\s+(?P<key>[^\s}]+)\s*\}\}'
    return re.findall(pattern, template)


def jinja2regexp(template, repl=r'(?P<\2>\\w+)'):
    # param = r'\{\{\s+(?P<key>[^\s}]+)\s*\}\}'
    # repl = r'(?P<\1>\\w+)'
    # pattern = re.sub(
    # param, repl, template, count=0, flags=0
    # ).replace(' ', '\s')

    # return pattern

    param = r'(\{\{\s+(?P<key>[^\s}]+)\s*\}\})'
    # repl = r'(?P<\2>' + wildcard + ')'
    pattern = re.sub(param, repl, template, count=0, flags=0).replace(
        ' ', '\s'
    )

    return pattern


def jinja2template(render, template, repl=r'(?P<\2>\\w+)', **ctx):
    params = jinja2params(template)
    mctx = {k: ctx[k] if k in ctx else '{{ ' + k + ' }}' for k in params}
    template = render(template).render(**mctx)

    pattern = jinja2regexp(template, repl)
    return pattern


def _hide_merge(a, b):
    # TODO: fix container merge, that seems not to merge individual values sometiems
    for key, value in walk(b):
        # path = '.'.join(key)
        container = new_container(value)
        if container is not None:
            value = container()

        spec = bspec(key)
        # for p in key:
        # spec = spec[p]
        current = glom(a, spec, default=None)
        print(f"{spec}: {current} --> {value}")
        setdefault(a, spec, value, missing=dict)
    foo = 1


class Executor:  # TODO Used??
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)

        self.ctx = {
            'prompt': '>> robot:',
        }
        self.executor = None
        self.interact = None
        self.prompt = None
        self.timeout = 60

    # def exec(self, cmd, **kw):
    # process = Popen(cmd, **kw)
    # stdout, stderr = process.communicate()
    # stdout = stdout.decode('utf-8')
    # return stdout

    async def expect(
        self, cmdline, default_match_prefix='.*\n', **reactions
    ):
        """
        cmdline is ephemeral

        output =
        ['ls /etc/sudoers.d/user_nopasswd',
        "ls: cannot access '/etc/sudoers.d/user_nopasswd': No such file or directory",
        '>> robot:']

        """
        reactions[self.ctx['prompt']] = 'prompt'
        reactions['.*password.*'] = 'sudo_passwd'

        options = list(reactions)
        inter = self.interact
        match = 0
        while True:
            match = inter.expect(
                options,
                timeout=self.timeout,
                default_match_prefix=default_match_prefix,
            )
            if match < 0:
                break
            token = reactions[options[match]]

            # prompt?
            if token in ('sudo_passwd',):
                self.interact.send(self.ctx['password'])
            elif token in ('prompt',):
                # ok, command execution finished
                output = inter.current_output
                output = output.lstrip(cmdline).rstrip(self.prompt).strip()
                # output = [line for line in output.splitlines() if line]
                return {token: output}
            else:
                foo = 1


class Handler:
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.hooks = {}
        self.ctx = {}

    def get_hook(self, state):
        assert isinstance(state, dict)
        blueprint = str(state)  # any hashable key
        blueprint = hashlib.md5(blueprint.encode('utf-8')).hexdigest()
        func = self.hooks.get(blueprint)
        if func is None:
            # we need to find the best handler for this state
            candidates = {}
            tokens = [f"{k}_{v}" for k, v in state.items()]
            # add wildcard 'any' to state values
            tokens.extend([f"{k}_any" for k in state])
            for attr in dir(self):
                # just analyze some pattern functions: _hook_xxx, do_xxx, in_xxx,
                if re.match(f'^(_hook|do|in)_.*', attr):
                    score = []
                    for token in tokens:
                        if re.search(token, attr):
                            if re.match(r'.*_any$', token):
                                value = 0.90
                            else:
                                value = 1
                        else:
                            value = 0

                        score.append(value)
                    candidates[sum(score)] = attr
            if candidates:
                best = max(candidates)
                self.hooks[blueprint] = func = getattr(
                    self, candidates[best]
                )
        return func


class Reactor:
    """
    - [ ] load plugins
    - [ ] provide a simple scheduler

    """

    def __init__(self, env=None):
        self.running = False
        self.stms = []
        self.tasks = []

        # custom 'env' on startup
        if env is None:
            env = {}
        self.ctx = {
            'hostname': platform.node(),
        }
        assign(self.ctx, bspec(ENV), env)

        try:
            self.log = logger(self.__class__.__name__.lower())
            self.console = self.log.debug
        except Exception as why:
            self.log.exception(why)
            self.log = None
            self.console = print

        # jinja templating
        template_dirs = [
            '.',
            './templates',
            os.path.join(os.path.split(__file__)[0], 'templates'),
        ]
        self.env = Environment(
            extensions=['jinja2.ext.do'],
            loader=FileSystemLoader(template_dirs),
            auto_reload=True,
        )

        # auto-inventory
        self.inventory = {}
        self.inventory_rules = {
            DEFAULT_EXECUTOR: {
                '__class__': r'.*DefaultExecutor.*',
            },
            ANY_CATEGORY: {
                '__class__.__name__': r'(?P<category>.*)',
            },
        }

    def add_inventory_rule(self, category, **criteria):
        self.inventory_rules[category] = criteria
        self._rebuild_inventory()

    def echo(self, pattern, _expand_=False, **kw):
        d = dict(self.ctx)
        d.update(kw)
        pattern = str(pattern)
        if _expand_:
            pattern = pattern.format_map(d)
        self.console(pattern)

    def notify(self, topic, value):
        self.log.info(f"""Notify: {topic}: '{value}'""")
        spec = bspec(RUN, topic)
        assign(self.ctx, spec, value, missing=dict)
        foo = 1

    def _rebuild_inventory(self):
        self.inventory.clear()
        for name, criteria in self.inventory_rules.items():
            for stm, info in self.find_stm(**criteria):
                category = info.get('category', name)
                key = info.get('key', stm.name)
                self.inventory.setdefault(category, {})[key] = stm
        foo = 1

    def attach(self, stm):
        self.stms.append(stm)
        stm.reactor = self
        try:
            if self.running:
                fiber = self.launch(stm)
                return fiber
        finally:
            self._rebuild_inventory()

    def detach(self, stm):
        if stm in self.stms:
            self.stms.remove(stm)
            # stm.reactor = None
        self._rebuild_inventory()

    def find_stm(self, **criteria):
        for item in self.stms:
            data = Finder.match(item, **criteria)
            if data:
                yield data  # item, info

        # def get(value, key):
        # for k in key.split('.'):
        # if value is not None:
        # value = getattr(value, k)
        # return value

        # for stm in self.stms:
        # match = [
        # re.search(pattern, str(get(stm, key)))  # is not None
        # for key, pattern in criteria.items()
        # ]
        # if all(match):
        # info = {}
        # for m in match:
        # info.update(m.groupdict())
        # yield stm, info

    def launch(self, stm):
        # add main() loop
        stm.state = STM.ST_INIT
        return self.new_fiber(stm.bootstrap())

    def new_fiber(self, func):
        fiber = create_task(func)
        self.tasks.append(fiber)
        return fiber

    async def main(self):
        console = self.log.debug if self.log else self.echo
        console(f">> {self.__class__.__name__} main(loop starting")
        self.running = True

        ## > debug
        # criteria = {
        ##'__name__': '.*PkgInstall',
        #'mro()': '.*PkgInstall.*',
        #'HANDLES': '.*pip.*',
        # }
        # kk = Finder.find_objects(**criteria)
        ## < debug
        for stm in self.stms:
            self.launch(stm)

        t1 = 0
        while self.tasks:
            t0 = time.time()
            if t0 > t1:
                console(
                    f"[{self.ctx['hostname']}] ------> Reactor has: {len(self.tasks)} tasks"
                )
                for i, stm in enumerate(self.stms):
                    self.log.debug(
                        f"  > [{i}]: {stm.__class__.__name__}:{stm.name}: state: {stm.state}"
                    )
                    t1 = time.time() + self.ctx.get('debug_lapse', 60)
            done, pending = await wait(
                self.tasks, timeout=5, return_when=FIRST_COMPLETED
            )
            for finished in done:
                self.tasks.remove(finished)

        # while self.running:
        # for agent in self.agents:
        # seconds = agent.pulse()
        # self.sleep(seconds)

        console(f"<< {self.__class__.__name__} main() loop ends")
        # self.save()

    def save(self, filename='reactor.yaml'):
        def str_presenter(dumper, data):
            try:
                dlen = len(data.splitlines())
                if dlen > 1:
                    # data = data.replace('\t', ' ')
                    return dumper.represent_scalar(
                        'tag:yaml.org,2002:str', data, style='|'
                    )
            except TypeError as ex:
                return dumper.represent_scalar('tag:yaml.org,2002:str', data)
            return dumper.represent_scalar('tag:yaml.org,2002:str', data)

        yaml.add_representer(str, str_presenter)
        yaml.representer.SafeRepresenter.add_representer(
            str, str_presenter
        )  # to use with safe_dum

        blueprint = {
            'include': {},
            'exclude': {
                r'\b_.+\b': '.*',
            },
        }
        data = self.search(blueprint, flat=False)

        os.makedirs(os.path.dirname(filename), exist_ok=True)
        yaml.dump(
            # self.ctx['real'],
            data,
            open(filename, 'wt'),
            Dumper=yaml.Dumper,
            # default_style="|",
        )
        foo = 1

    def search(self, blueprint, center=[], flat=True):
        return search(self.ctx, blueprint, center, flat)


class LAMBDA_NOT_FOUND:
    pass


class STM:
    # states
    ST_SAME = '{state}'
    ST_NEW = '{new_state}'  #  TODO: used?
    ST_INIT = 'init'
    ST_BOOT = 'boot'
    ST_READY = 'ready'
    ST_RUNNING = 'running'
    ST_RESTART = 'restart'
    ST_STOP = 'stop'
    ST_IDLE = 'idle'
    ST_KILL = 'kill'
    ST_ANY = '.*'
    ST_LAST = '{saved_state}'

    # events
    EV_NOP = 'None'
    EV_IDLE = 'Idle'
    EV_READY = 'Ready'
    EV_RUNNING = 'Running'
    EV_RESTART = 'Restart'
    EV_IDLE = 'Idle'
    EV_TERM = 'Term'
    EV_WAIT = 'Wait'
    EV_RESUME = 'Resume'
    EV_KILL = 'Kill'
    EV_CONNECT = 'Connect'
    EV_DISCONNECT = 'Disconnect'

    # actions
    DO_SAME = '{new_st}'
    DO_EXIT = 'exit_{st}'
    DO_RESTART = 'restart_{st}'
    DO_CONNECT = 'connect'
    DO_SEQUENTIAL = 'sequential'
    DO_IDLE = 'idle'

    PRE_ALWAYS = []

    def __init__(self, name=None, restart=-1, *args, **kw):
        super().__init__()

        self.name = name or f'{self.__class__.__name__}_{id(self)}'
        self.restart = restart

        self.ctx = dict(self.__dict__)
        self.ctx.update(kw)
        self.ctx.setdefault('local_hostname', platform.node())

        self.running = False
        self.reactor = None

        self.queue = Queue()
        self.state = self.ST_INIT
        self.transitions = {}
        self.allow_events = {}
        self._hooks = {}
        self._stage_cache = {}
        self._seq_topic_active = {}
        self._stop_no_seq = (
            True  #  stop STM when _seq_topic_active are active
        )

        self.t0 = None
        self.t1 = None

        self._build_transitions()

        self.log = logger(self.__class__.__name__.lower())
        foo = 1

    # --------------------------------------------------
    # custom transition callbacks
    # --------------------------------------------------
    @property
    def is_done(self):
        return self.state in (self.ST_KILL)

    @property
    def is_active(self):
        return not self.is_done

    def get_ctx(self, **kw):
        ctx = dict(self.__dict__)
        ctx.update(self.ctx)
        ctx.update(kw)
        return ctx

    def g(self, *spec, default=None, _target_=None):
        if _target_ is None:
            _target_ = self.reactor.ctx
        spec = bspec(*spec)
        return glom(_target_, spec, default=default)

    def g_old(self, *spec, default=None, _target_=None):
        if _target_ is None:
            _target_ = self.reactor.ctx
        spec = tspec(*spec)
        return glom(_target_, spec, default=default)

    def s(self, spec, value, missing=dict, _target_=None, **kw):
        if _target_ is None:
            _target_ = self.reactor.ctx
        spec = bspec(spec)
        assign(_target_, spec, value, missing=missing, **kw)

    def search(self, blueprint, center=[], flat=True):
        return search(self.reactor.ctx, blueprint, center, flat)

    def gather_values(self, *specs, **blueprint):
        target = self.g(bspec(specs))
        return gather_values(target, **blueprint)

    def m(self, spec, value, missing=dict, _target_=None, **kw):
        spec = bspec(spec)
        holder = self.g(spec, default={}, _target_=_target_)
        merge(holder, value, inplace=True)

    def load(self, path):
        data = yaml.load(open(path), Loader=yaml.Loader)
        return data

    def notify(self, topic, value):
        self.reactor.notify(topic, value)

    def build_ctx(self, *args, **kw):
        ctx = dict(self.reactor.ctx)
        ctx.update(self.g('env'))
        ctx.update(self.__dict__)
        ctx.update(self.ctx)
        for item in args:
            if isinstance(item, dict):
                ctx.update(item)
        ctx.update(kw)
        ctx['local_uid'] = os.geteuid()
        ctx['local_gid'] = os.getgid()
        return ctx

    def subset(
        self,
        container,
        include_keys=[],
        exclude_keys=[],
        include_values=[],
        exclude_values=[],
        default=None,
        **kw,
    ):
        def explore():
            render = self.reactor.env.from_string
            repl = r'(?P<\2>\\w+)'
            wildcard = r'[^\.]+'
            for key, value in walk(container):
                spec = '.'.join([str(k) for k in key])
                ctx = self.build_ctx(**kw)
                # include keys
                if include_keys:
                    abort = True
                    for template in include_keys:
                        # replace known params
                        pattern = jinja2template(render, template, **ctx)
                        m = re.match(pattern, spec)
                        if m:
                            ctx.update(m.groupdict())
                            abort = False
                    if abort:
                        continue
                # include values
                if include_values:
                    abort = True
                    for template in include_values:
                        pattern = jinja2template(render, template, **ctx)
                        m = re.match(pattern, str(value))
                        if m:
                            ctx.update(m.groupdict())
                            abort = False
                    if abort:
                        continue

                # exclude keys
                if exclude_keys:
                    abort = False
                    for template in exclude_keys:
                        pattern = jinja2template(render, template, **ctx)
                        m = re.match(pattern, spec)
                        if m:
                            abort = True
                            break
                    if abort:
                        continue

                # exclude values
                if exclude_values:
                    abort = False
                    for template in exclude_values:
                        pattern = jinja2template(render, template, **ctx)
                        m = re.match(pattern, str(value))
                        if m:
                            abort = True
                            break
                    if abort:
                        continue

                # key (spec) is accepted
                yield key, value

        # result = list(explore())
        # result = rebuild(result, result={})

        result = rebuild(explore(), result={})
        return result

    def push(self, event, **kw):
        self.queue.put_nowait((event, kw))

    def _term(self, *args, **kw):
        self.push(self.EV_TERM)

    def _kill(self, *args, **kw):
        self.push(self.EV_KILL)

    def find_method(self, regexps):
        if isinstance(regexps, str):
            regexps = [regexps]
        for name in dir(self):
            for regexp in regexps:
                m = re.match(regexp, name)
                if m:
                    func = getattr(self, name)
                    if inspect.iscoroutinefunction(func):
                        yield func, m.groupdict()
                        break

    def my_tasks(self, skip_internal=True):
        if skip_internal:
            internals = set(
                [id(f.__func__.__code__.co_code) for f in (self.main,)]
            )
        else:
            internals = set()
        for task in self.reactor.tasks:
            if task.done():
                continue
            instance = task._coro.cr_frame.f_locals.get('self')
            if id(instance) == id(self):
                if id(task._coro.cr_code.co_code) not in internals:
                    yield task

    async def bootstrap(self):
        assert isinstance(self.reactor, Reactor)

        self.running = True

        # automatic launch any _boot fiber
        bootstrap = []
        for func, d in self.find_method(r'_boot_.*'):
            bootstrap.append(self.reactor.new_fiber(func()))

        # wait until all bootstrap fibers has finished
        if bootstrap:
            await wait(bootstrap)
            foo = 1

        # launch main and domestic fibers
        self.reactor.new_fiber(self.main())
        for func, d in self.find_method(r'_fiber_.*'):
            self.reactor.new_fiber(func())

        foo = 1

    async def _sequential_execution(self, topic, sequence, retry=20):
        result = True  # chain
        for func, d in sequence:
            iid = self.__class__.__name__.lower()
            spec = tspec(iid, topic)
            self.notify(spec, d.get('sub'))

            if not self.running:
                break

            while result:
                # launch fiber
                self.log.info(f"launching fiber: '{func.__name__}'")
                fiber = self.reactor.new_fiber(func(result=result))

                try:
                    while self.running and not fiber.done():
                        await self.sleep(1.0)
                except Exception as why:
                    self.log.exception(why)
                    self.log.error(f"Retrying in {retry}")
                    await self.sleep(retry)
                    continue

                if self.running:
                    result = fiber.result()
                    if not result:
                        self.log.warning(
                            f"sequential chain aborted: '{func.__name__}' returns false condition"
                        )
                else:
                    self.log.warning(
                        f"{self} is prematurelly set to {self.state}, aborting sequential execution"
                    )
                break

            # next one!

        self.notify(spec, 'done')
        self._seq_topic_active[topic] = False
        if (
            self._stop_no_seq
            and self._seq_topic_active
            and not all(self._seq_topic_active.values())
        ):
            self.log.warning(
                f"{self.name} has finished all sequential ({len(self._seq_topic_active)}) fibers and _stop_no_seq={self._stop_no_seq}, so will stop ASAP"
            )
            self.push(self.EV_TERM)

        self.log.warning(f"{self.name} has restart: {self.restart}")
        return result

    async def main(self):
        """
        - get event
        - get transitions(event)
           - assert just 0-1 transition has been found (no more)
        - execute exit_{state} functions
        - execute user transition functions (defined in transition)
        - execute default transition functions: do_{state}_{new_state}
        - execute enter_{new_state} functions (state is not yet changed)
        - then change state

        Notes:

        - enter_{state} and exit_{state} are always executed almost once
        - do_{state} is only executed when is looping {state} --> {same state}
        - do_{state}_{new_state} are executed within transition just once (not looping)

        """
        assert self.running == True, "call main() before bootstrap() ??"
        self.t0 = time.time()
        t2 = self.t0 + 3

        # event auto-stimulation
        auto = set(
            [
                self.EV_NOP,
            ]
        )

        while self.running:
            self.t1 = time.time()
            if self.queue._queue:
                fqevent = await self.queue.get()
            else:
                # event auto-stimulation
                auto_event = auto.intersection(
                    self.allow_events.get(self.state, {})
                )
                params = {}
                for event in auto_event:
                    fqevent = tuple([event, params])
                    break
                else:
                    seconds = self.ctx.get('sleep', 1.0)
                    fqevent = await self.get_event(seconds)

            transitions = self.get_transitions(fqevent)
            event, params = fqevent  # TODO: use **params

            # self.log.debug(
            # f"--> {self.name}: state: '{self.state}' event={event}"
            # )

            # self.log.debug(f"    transitions: {transitions}")
            # if len(transitions) > 1:

            if len(transitions) > 1:
                raise RuntimeError(
                    f"DBEUG: Multiples transitions for event: {event} in state: {self.state}"
                )

            await self.dispatch('exit', self.state, **params)
            foo = 1
            for d in transitions.values():
                assert (
                    len(list(d.values())) <= 1
                ), f"[{self.__class__.__name__}: {self.name}]: multiples transitions are available from state: `{self.state}` with event: `{event}` --> {d}"
                for self.new_state, callbacks in d.items():
                    # add default transition from state -> new_state
                    # if self.state in (self.new_state,):
                    # base_callbacks = f'{self.state}'
                    # else:
                    # base_callbacks = f'{self.state}_{self.new_state}'

                    func1 = f'{event}_{self.state}_{self.new_state}'
                    func2 = f'{event}'

                    # if 'Servic' in self.name:
                    # self.log.warning(
                    # f"  - transition '{self.state}' --> '{self.new_state}', applying do_{callbacks} lambdas"
                    # )
                    # foo = 1

                    # dispatch func
                    await self.dispatch(
                        'do', func1, func2, *callbacks, **params
                    )
                    if self.new_state in (self.ST_SAME,):
                        # TODO: used now?
                        self.new_state = self.state

                    self.state, self.new_state = self.new_state, None

            await self.dispatch('enter', self.state, **params)

            #
            #  check if the STM has not any other working task
            if self.t1 > t2:
                mytask = list(self.my_tasks())
                events = self.queue.qsize()
                trace.debug(
                    f"'{self.name}' state: ['{self.state}'] has '({len(mytask)})' tasks and '({events})' events pending"
                )
                t2 = self.t1 + 3
                if len(mytask) == 1:
                    foo = 1
                    # self.push(self.EV_TERM)

                # print some running STM actions
                for i, task in enumerate(mytask):
                    self.log.debug(f"  - task:[{i}]: {task}")

                foo = 1

        self.log.warning(f"< {self.name} exit: {self.state}")

    async def get_event(self, timeout=0.2):
        while timeout > 0:
            if self.queue.empty():
                pause = min(timeout, 1)
                timeout -= pause
                await self.sleep(pause)
            else:
                return await self.queue.get()
        return self.EV_IDLE, {}

    def get_transitions(self, event):
        candidates = {}
        # ctx = dict(self.ctx)
        ctx = self.get_ctx()
        state = str(self.state)  # TODO: property?
        event, kw = event  # TODO: use kw in ctx?
        event = str(event)
        ctx['state'] = state
        ctx['st'] = state
        ctx['event'] = event
        for _state_a, transitions in self.transitions.items():
            _state_a = _state_a.format_map(ctx)
            if re.match(_state_a, state):
                for (
                    _event,
                    trx,
                ) in transitions.items():
                    if re.match(_event, event):
                        for (
                            _state_b,
                            preconditions,
                            lambdas,
                        ) in trx:
                            _state_b = _state_b.format_map(ctx)
                            # filter preconditions
                            ctx['new_state'] = _state_b
                            ctx['new_st'] = _state_b

                            preconditions = [
                                eval(exp.format_map(ctx), ctx)
                                for exp in preconditions
                            ]
                            if not preconditions or all(preconditions):
                                lambdas = [
                                    func.format_map(ctx) for func in lambdas
                                ]
                                if lambdas:
                                    foo = 1
                                candidates.setdefault(
                                    _state_a, {}
                                ).setdefault(_state_b, []).extend(lambdas)

        return candidates

    async def dispatch(self, stage, *callbacks, **kw):
        coros = self._get_coros(stage, *callbacks, **kw)
        return await self._wait_coros(coros)

    async def _wait_coros(self, coros):
        try:
            if coros:
                await wait(coros)
        except Exception as why:
            self.log.exception(why)
            foo = 1
        foo = 1

    def _get_coros(self, stage, *callbacks, **kw):
        # self.echo(f"    - searching for: '{stage}'_{callbacks} tasks")
        assert len(callbacks) == len(
            set(callbacks)
        ), f"duplicated callbacks!: {callbacks}"

        tasks = [self.get_hook(name, stage) for name in callbacks if name]
        # self.echo(f"    - tasks: {tasks}")

        # remove duplicates, but preserving order
        unique = []
        coros = []
        for coro in tasks:
            if coro and coro not in unique:
                unique.append(coro)
                coros.append(create_task(coro(**kw)))

        return coros

    def _get_stage_methods(self, stage):
        methods = self._stage_cache.get(stage)
        if methods is None:
            methods = self._stage_cache[stage] = []
            for attr in dir(self):
                # just analyze some pattern functions: _hook_xxx, do_xxx, in_xxx,
                m = re.match(f'^(_+)?({stage})_(.*)', attr)
                if m:
                    tokens = m.group(3)
                    tokens = tokens.split('_')
                    methods.append((tokens, attr))
        return methods

    def get_hook(self, name, stage='do'):
        blueprint = f'{stage}_{name}'  # any hashable key
        # blueprint = hashlib.md5(blueprint.encode('utf-8')).hexdigest()
        func = self._hooks.get(blueprint, LAMBDA_NOT_FOUND)
        if func is LAMBDA_NOT_FOUND:
            # we need to find the best handler for this state
            candidates = {}

            # TODO: future, allow more complex func name patterns
            names = name.split('_')
            lnames = len(names) or 1
            patterns = []
            seq = []
            for t in names:
                seq.append(t)
                patterns.append(list(seq))

            patterns.reverse()
            # tokens = list(
            # itertools.accumulate(names, func=lambda x, y: x + "_" + y)
            # )
            # tokens.reverse()

            # add wildcard 'any' to state values
            # TODO: cache methods that match 'stage' for faster iteration
            # tokens.extend([f"{k}_any" for k in state])
            # just analyze some pattern functions: _hook_xxx, do_xxx, in_xxx,

            for tokens, attr in self._get_stage_methods(stage):
                for score, patt in enumerate(patterns):
                    sc = likelyhood6(patt, tokens)
                    # sc = likelyhood5(patt, tokens)
                    candidates[score + sc] = attr
                else:
                    pass  #  not found

            func = None
            if candidates:
                best = min(candidates)
                if best < 1.0:
                    func = getattr(self, candidates[best])
                else:
                    func = None

            self._hooks[blueprint] = func
        return func

    def add_transition(
        self,
        state_a,
        event,
        state_b,
        preconditions=[],
        lambdas=[],
    ):
        if preconditions or lambdas:
            foo = 1

        if lambdas:
            if isinstance(lambdas, str):
                lambdas = [lambdas]

            foo = 1

        # inverse map
        record = preconditions, lambdas
        holder = (
            self.allow_events.setdefault(state_a, {})
            .setdefault(event, {})
            .setdefault(state_b, [])
        )
        if record not in holder:
            holder.append(record)

        # direct map
        holder = self.transitions.setdefault(state_a, {}).setdefault(
            event, []
        )

        transition = [state_b, preconditions, lambdas]
        if transition not in holder:
            holder.append(transition)
        else:
            print(
                f"transition {transition} already added for {state_a} : -> {event}"
            )

    # helpers
    def echo(self, pattern, _expand_=False, **kw):
        self.reactor and self.reactor.echo(pattern, _expand_, **kw)
        pass

    async def sleep(self, seconds=None):
        # date = datetime.now()
        pause = self.ctx.get('sleep', 5)
        if seconds is None:
            seconds = (0.1 + random.random()) * pause
        # self.echo(f"{date} sleeping for {seconds} seconds ...")
        # self.save_config()
        # HACK for easyly reconnect remote debugger
        while seconds > 0:
            await sleep(min(seconds, 2))
            seconds -= 1

    def reset_counter(self, name, value=0):
        self.ctx[name] = value
        return self.ctx[name]

    def inc_counter(self, name, delta=1, top=10**6):
        self.ctx[name] = min(top, self.ctx.get(name, 0) + delta)
        return self.ctx[name]

    def hurryup(self, pattern=None):
        self.reset_counter('sleep', value=0)
        if pattern is not None:
            for stm in self.reactor.stms:
                if option_match(pattern, stm.name, str(stm)):
                    stm.hurryup()

    def slowdown(self):
        self.inc_counter('sleep', delta=1, top=90)

    # --------------------------------------------------
    # Transitions
    # --------------------------------------------------
    def _build_transitions(self):
        s = self
        # --------------------------------------------------
        # Basic STM definition
        # --------------------------------------------------
        s.add_transition(s.ST_INIT, s.EV_NOP, s.ST_BOOT)
        s.add_transition(
            s.ST_BOOT, s.EV_READY, s.ST_READY, s.PRE_ALWAYS, s.DO_SEQUENTIAL
        )
        s.add_transition(s.ST_READY, s.EV_RUNNING, s.ST_RUNNING)

        # --------------------------------------------------
        # Terms from any state
        # --------------------------------------------------
        s.add_transition(
            s.ST_ANY,
            s.EV_TERM,
            s.ST_STOP,
            ['not (_seq_topic_active and any(_seq_topic_active.values()))'],
        )
        s.add_transition(
            s.ST_ANY,
            s.EV_TERM,
            s.ST_IDLE,
            ['_seq_topic_active and any(_seq_topic_active.values())'],
        )
        s.add_transition(s.ST_ANY, s.EV_KILL, s.ST_KILL)
        s.add_transition(s.ST_STOP, s.EV_NOP, s.ST_KILL, ['restart <= 0'])
        s.add_transition(s.ST_STOP, s.EV_NOP, s.ST_RESTART, ['restart > 0'])

        # --------------------------------------------------
        # Restart from any state
        # --------------------------------------------------
        s.add_transition(s.ST_ANY, s.EV_RESTART, s.ST_RESTART)
        s.add_transition(s.ST_RESTART, s.EV_NOP, s.ST_INIT)

        # --------------------------------------------------
        # Wait/Resume from any state
        # --------------------------------------------------
        s.add_transition(s.ST_ANY, s.EV_WAIT, s.ST_IDLE)
        s.add_transition(s.ST_IDLE, s.EV_RESUME, s.ST_LAST)

        # --------------------------------------------------
        # Reconnect (whatever means) if has been disconnected in any state
        # --------------------------------------------------
        s.add_transition(s.ST_ANY, s.EV_DISCONNECT, s.ST_SAME)
        s.add_transition(s.ST_ANY, s.EV_IDLE, s.ST_SAME)

    # --------------------------------------------------
    # Common transition callbacks
    # --------------------------------------------------
    # Idle
    async def do_Idle(self, *args, **kw):
        """Executed on every idle event, any state"""
        pause = self.ctx.get('sleep', 2)
        await self.sleep(pause)
        self.slowdown()

    # boot
    async def do_None_init_boot(self, *args, **kw):
        """From 'init' --> 'boot', any event"""
        pass

    async def _enter_boot(self, *args, **kw):
        """Pre-call for 'boot' state"""
        self.log.debug(
            f"{self.__class__.__name__}: _enter_boot: '{self.name}'"
        )
        self.ctx['sleep'] = 1
        self.push(self.EV_READY)

    # ready
    async def _enter_ready(self, *args, **kw):
        """
        Performs any bootstrap action needed
        """
        self.push(self.EV_RUNNING)

    async def do_Wait(self, *args, **kw):
        self.ctx['saved_state'] = self.state

    # running
    async def do_Idle_running_running(self, *args, **kw):
        await self.sleep(1)

    # restart
    async def do_Restart(self, *args, **kw):
        self.log.debug(f"do_Restart: STM '{self}': {args} : {kw}")

    async def _enter_restart(self, *args, restart=None, **kw):
        """Pre-call for 'restart' state"""
        restart = restart or self.restart
        assert restart > 0
        self.log.debug(f"waiting {restart} before going init ...")
        await self.sleep(restart)
        foo = 1

    # kill
    async def _enter_kill(self):
        self.echo(f"Killing {self.__class__.__name__}:{self.name} !!")
        self.running = False
        self.reactor.detach(self)

    # Term
    async def _enter_stop(self, *args, **kw):
        if any(self._seq_topic_active.values()):
            self.log.error(
                f"{self.name} has sequential topics still running, going to IDLE state"
            )
            # self.push(self.EV_WAIT) # is not possible now to revert (None event may trigger)

    async def _enter_idle(self, *args, **kw):
        self.log.debug(f"{self} entering in IDLE state")
        foo = 1

    # --------------------------------------------------
    # custom transition callbacks
    # --------------------------------------------------

    async def do_sequential(self, *args, **kw):
        """
        Performs any bootstrap action needed
        """
        # launch sequential fibers
        lines = {}
        for func, d in self.find_method(
            r'_seq_(?P<key>[^_]+)(_(?P<topic>[^_]*))?(_(?P<sub>.*?))?$'
        ):
            lines.setdefault(d['topic'], list()).append((func, d))

        for topic, sequence in lines.items():
            sequence.sort(key=lambda x: x[0].__name__)
            self.log.debug(f"launching: '{topic}'")
            for i, seq in enumerate(sequence):
                self.log.debug(f"[{i}] {seq[0].__func__.__name__}")
            self.reactor.new_fiber(
                self._sequential_execution(topic, sequence)
            )
            self._seq_topic_active[topic] = True


def norm_key(text):
    return text.strip().lower().replace(' ', '_')


def norm_mode(text, **kw):
    if isinstance(text, str):
        return int(text)


CONVERTERS = {
    r'\.fs\..*\.mode.*': norm_mode,
}


def norm_val(text, fqkey=[]):
    if not isinstance(text, str):
        text = str(text)
    text = text.strip().lower()

    # remove ANSI TERM escape sequences
    m = re.search('\x1b\[32m(.*)\x1b', text)
    if m:
        text = m.group(1)

    fqkey = tspec(fqkey)
    # particular cases
    key = '.'.join(fqkey)
    for pattern, func in CONVERTERS.items():
        m = re.search(pattern, key)
        if m:
            d = m.groupdict(default='')
            text = func(text, **d)

    return text


def test_deamon():
    class Date(Agent):
        async def do_state_idle(self, **kw):
            self.echo(f"{self.name} is idle !!")
            if random.random() < 0.35:
                await self.kill()
            if random.random() < 0.25:
                self.echo(f"{self.name} launch another fiber !!")
                await self.reactor.launch(self)

    reactor = Reactor()
    for i in range(3):
        shell = Action()
        agent = Date(f'agent-{i}', shell=shell)
        reactor.attach(agent)

    run(reactor.main())
    foo = 1


def test_stm():
    class SimpleSTM(STM):
        def __init__(self, *args, **kw):
            super().__init__(*args, **kw)

            self.add_transition('init', 'None', 'idle', 'hello')
            self.add_transition('idle', 'None', 'idle', 'hello')

        async def do_hello(self):
            counter = self.inc_counter('foo')
            self.echo(f"[{counter}] hello world!!")
            if counter > 5:
                await self.kill()

    reactor = Reactor()
    for i in range(1):
        stm = SimpleSTM()
        stm.ctx['sleep'] = 0.1
        reactor.attach(stm)

    run(reactor.main())


class ShellSTM(STM):
    """
    Can run commands"""

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)

    def local_exec(self, pattern, **kw):
        stack = inspect.stack()
        context = dict(stack[1].frame.f_locals)
        context.update(**kw)
        context.pop('self')
        cmd = self.expand(pattern, **context)
        self.log.debug(f"executing: {cmd}")
        r = shutil.os.system(cmd)
        return r

    def expand(self, template, **kw):
        ctx = self.build_ctx(**kw)
        params = set(jinja2params(template))
        template = self.reactor.env.from_string(template)
        while params:
            # try to locate missing params searching across stack frames
            stack = inspect.stack()
            frame = stack[1].frame
            missing = params.difference(ctx)
            while frame and missing:
                f_locals = frame.f_locals
                for attr in missing.intersection(f_locals):
                    ctx[attr] = f_locals[attr]
                    missing.remove(attr)
                frame = frame.f_back

            template = template.render(**ctx)
            params = set(jinja2params(template))
            template = self.reactor.env.from_string(template)

        template = template.render(**ctx)
        return template

    @property
    def default_executor(self):
        for stm in self.reactor.inventory.get(DEFAULT_EXECUTOR, {}).values():
            return stm


CONNECTION_IN_PROGRESS = 'connection_in_progress'


class DefaultExecutor(ShellSTM):
    def __init__(self, host='localhost', retry=10, *args, **kw):
        super().__init__(*args, **kw)
        self.host = host
        self.connection = None
        self.process = []
        self.ctx['host'] = host
        self.retry = retry
        self.trying = False

        self.log_commands = logger('commands')

    @property
    def isremote(self):
        if self.connection:
            return self.connection._peer_addr not in ('127.0.0.1',)

    @property
    def user(self):
        return self.ctx.get('user') or getpass.getuser()

    def _build_transitions(self):
        super()._build_transitions()
        # s.add_transition(s.ST_BOOT, s.EV_READY, s.ST_READY, s.DO_SAME)

    async def create_process(self, cmdline, *args, **kw):
        while True:
            try:
                process = await self.connection.create_process(cmdline, **kw)

                break
            except Exception as why:
                self.log.error(f"{why} while trying: '{cmdline}'")
                await self.sleep(5)
                foo = 1
        self.process.append(process)
        return process

    def connection_lost(self, *args, **kw):
        self.log.error(f"{args}, reconnecting....")
        self.connection = None
        self.push(self.EV_DISCONNECT)
        foo = 1

    async def milk(self, process):
        _stdout = process._stdout
        _session = _stdout._session
        output = ''
        size = 1
        while process.exit_status is None or size > 0:
            if size <= 0:
                await self.sleep()
            output += await _stdout.read(size)
            size = _session._recv_buf_len

        return output

    async def exec_many(self, *commands, sudo=True, **ctx):
        candidates = ['', 'sudo '] if sudo else ['']

        for su in candidates:
            try:
                for cmd in commands:
                    cmd = self.expand(cmd, **ctx)
                    # template = self.reactor.env.from_string(cmd)
                    # cmd = template.render(**ctx)
                    cmd = f'{su}{cmd}'

                    process = await self.create_process(cmd, stderr=STDOUT)
                    output = await self.milk(process)
                    if process.exit_status != 0:
                        self.log.warning(
                            f"Executing: '{cmd}' FAILED: {output}"
                        )
                        break
                    self.log.info(f"Executing: '{cmd}' Ok, output={output}")
                else:
                    return True
            except Exception as why:
                self.log.exception(why)
        else:
            why = f"Error executing commands {commands}"
            self.log.error(why)
            # raise RuntimeError(why)

        return False

    async def scp(self, source, target):
        # TODO: reuse self.connection
        # TODO: guess put/get and apply
        await asyncssh.scp(source, target)
        foo = 1

    async def put(self, source, target):
        self.log.debug(f"PUT {source} ---> {self.connection._host}:{target}")
        self.log_commands.info(
            f"PUT {source} ---> {self.connection._host}:{target}"
        )

        await asyncssh.scp(source, (self.connection, target))
        foo = 1

    async def get(self, source, target):
        """
        - copy the file using connection user or sudo to a temporal location
        - give read permission
        - get temporal file
        - remove temporal file
        """
        self.log.debug(f"GET {target} <--- {self.connection._host}:{source}")
        self.log_commands.info(
            f"GET {target} <--- {self.connection._host}:{source}"
        )
        try:
            result = await asyncssh.scp((self.connection, source), target)
        except asyncssh.sftp.SFTPFailure as why:
            temp = temp_filename()
            result = await self.exec_many(
                "sudo cp {{ source }} {{ temp }}",
                "sudo chmod 444 {{ temp }}",
            )
            try:
                await asyncssh.scp((self.connection, temp), target)
            except Exception:
                result = False
            finally:
                await self.exec_many("sudo rm {{ temp }}")
            foo = 1
        except Exception as why:
            self.log.exception(why)
            return False
        return result

    # --------------------------------------------------
    # Common transition callbacks
    # --------------------------------------------------
    async def _enter_boot(self, *args, **kw):
        """
        Performs any bootstrap action needed
        """
        self.echo(f"{self.name} is booting!!")
        # r_ctx = self.reactor.ctx
        # conn = r_ctx.get(DEFAULT_CONNECTION)
        # Get everything sorted before going on
        if self.connection is None:
            self.push(self.EV_DISCONNECT)
        else:
            await super()._enter_boot()

    # Disconnect
    async def do_Disconnect(self):
        self.log.debug(f"{self.name} connecting to {self.host}!!")
        if self.trying:
            if self.retry > 0:
                self.log.debug(
                    f"Last conntecion attempt was failed. Retraying again."
                )
            else:
                self.log.debug(
                    f"Last conntecion attempt was failed. Do not retry as retry={self.retry} <=0"
                )
                self.push(self.EV_KILL)
                return

        if self.connection:
            self.log.debug(
                f"ignoring duplicated {self.EV_CONNECT} events ..."
            )
            return

        # r_ctx = self.reactor.ctx
        # self.connection = r_ctx.get(DEFAULT_CONNECTION)
        # assert conn is None

        # username, password, client_keys, known_hosts
        # m = re.match(
        # r'(((?P<username>[\w]+)(:(?P<password>\w+))?)@)?(?P<host>[\w]+)',
        # self.host,
        # )
        # if m:
        # params = {
        # k: v
        # for k, v in m.groupdict(default=None).items()
        # if v is not None
        # }
        # else:
        # params = dict(hostname=self.host)

        params = {
            k: self.ctx.get(k)
            for k in [
                'host',
                'user',
                'password',
                'client_keys',
                #'known_hosts',
            ]
        }
        params['username'] = params.pop('user', None)
        params = {k: v for k, v in params.items() if v}
        # self.ctx.update(params)
        # LANG=en_US.UTF-8
        # !LANG !LC_*
        # params['options'] = {'LANG': 'en_US.UTF-8'}
        # sudo update-locale LANG=en_US.UTF-8 LC_MESSAGES=POSIX
        options = SSHClientConnectionOptions()
        options.keepalive_interval = 2
        params['options'] = options
        retry = self.retry
        self.trying = True
        try:
            self.log.debug(f"Connect using: {params}")
            self.connection = await asyncssh.connect(
                known_hosts=None, **params
            )
        except OSError as why:
            if self.retry > 0:
                reason = f"Unable to connect: {params}, retrying in {retry}"
                self.log.warning(reason)
                self.connection_lost(reason)
                await self.sleep(retry)
            else:
                self.push(self.EV_KILL)
            return
        self.reactor.ctx[DEFAULT_CONNECTION] = self.connection

        # debug

        c = (
            self.connection
        )  # <class 'asyncssh.connection.SSHClientConnection'>
        c.connection_lost = self.connection_lost
        c._keepalive_interval = 2

        proc = await c.create_process(r'hostname', stdout=PIPE)
        hostname = await proc._stdout.read()
        self.reactor.ctx[
            'observed_hostname'
        ] = self.observed_hostname = hostname.strip()

        if 'password' in params:
            params['password'] = '*' * len(params['password'])
        self.log.info(
            f"Connected to: '{c._host}', peer: {c._peer_addr}:{c._peer_port}: {params}"
        )
        self.log.warning(f"hostname returned: '{self.observed_hostname}'")
        self.trying = False
        foo = 1

    async def do_Idle_running_running(self, *args, **kw):
        # self.log.debug(f"{self.name} is ready!!")

        foo = 1
        self.process = [p for p in self.process if p.exit_status is None]
        # check if no other task is running
        if len(self.reactor.tasks) == 1:
            self.log.debug(f"No more task, so stopping executor")

            self.connection = None
            self.push(self.EV_TERM)

        await super().do_Idle_running_running(*args, **kw)
        foo = 1


# ------------------------------------------------
# Finder
# -----------------------------------------------


class Finder:
    CACHE = {}

    @classmethod
    def find_objects(cls, **criteria):
        blueprint = list(criteria.items())
        blueprint.sort()
        blueprint = tuple(blueprint)
        if blueprint not in cls.CACHE:
            for name, module in list(sys.modules.items()):
                for attr in dir(module):
                    try:
                        item = getattr(module, attr, None)
                    except Exception as why:
                        print(f"{RED}Error: {why}{RESET}")
                        continue
                    # if "PkgInstall" in str(item):
                    # foor = 1
                    data = cls.match(item, **criteria)
                    if data:
                        cls.CACHE.setdefault(blueprint, set()).add(item)

        return cls.CACHE.get(blueprint, set())

    @classmethod
    def match(cls, item, **criteria):
        def get(value, key):
            for k in key.split('.'):
                if value is None:
                    break
                try:
                    value = eval(f'value.{k}')
                    foo = 1
                except Exception:
                    try:
                        value = getattr(value, k, None)
                        # if inspect.isroutine(value):
                        # value = value()
                    except Exception:
                        return None
            return value

        match = [
            re.match(pattern, str(get(item, key)))  # is not None
            for key, pattern in criteria.items()
        ]
        if all(match):
            info = {}
            for m in match:
                info.update(m.groupdict())
            return item, info


if __name__ == '__main__':
    # test_files()
    # test_modem_from_sample()
    # test_modem_already_configured()
    # test_modem_unconfigured()
    # test_configure_modem_from_scratch()

    # test_deamon()
    # test_stm()
    # test_deb_packages()
    # test_pip_packages()

    foo = 1
