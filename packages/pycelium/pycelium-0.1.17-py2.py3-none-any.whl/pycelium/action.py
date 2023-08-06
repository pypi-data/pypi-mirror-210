import sys
import os
import re
import hashlib
import random
import time
import inspect
from subprocess import Popen, PIPE, STDOUT


from .definitions import (
    DEB_FACTS,
    REAL,
    TARGET,
    PIP_FACTS,
    SERVICE_FACTS,
    setdefault,
    DEFAULT_EXECUTOR,
)

from .tools.calls import scall
from .tools.logs import logger


from .shell import (
    STM,
    assign,
    bspec,
    tspec,
    update,
    walk,
    glom,
    T,
    Finder,
    jinja2regexp,
    temp_filename,
    ShellSTM,
    DefaultExecutor,
)


class Action(ShellSTM):
    """
    A simple STM

    ctx: context
    command: { key : ( cmd_template, [response_regexp]) }

    history = []
    out = []
    process = []
    MAX_HISTORY: 50

    """

    # user can control what is the remainin part
    # adding this token to the regexp
    # otherwise an automatic parameter is added
    # to the user regexp for capturing remainig
    # output
    REMAIN = '__remain__'
    MAX_HISTORY = 50

    state: str

    EV_SUDO = 'Sudo'

    def __init__(
        self,
        cmdline='',
        pattern='',
        restart=-1,
        partial='',
        sudo=True,
        nice=True,
        warm_body=60,
        *args,
        **kw,
    ):
        super().__init__(restart=restart, *args, **kw)
        self.ctx = kw
        self.commands = {}

        self.actions = {}

        self.dry = False  # TODO: implement

        self.pattern = pattern
        self.sudo = sudo
        self.nice = nice
        self.warm_body = warm_body

        self.cmdline = cmdline
        self.partial = partial
        self.reg_depth = 1024 * 1
        self.seen = ''
        self.interactions = {}
        self.progress = 0
        self.history = []
        self.progress = None
        self.process = None
        # self.outgoing = []

        self.console = print
        self.log_commands = logger('commands')

        # add custom filters to jinja
        # self.env.filters['tohardness'] = tohardness
        # self.env.filters['todate'] = date_to_text
        # self.env.filters['toduration'] = duration_to_text
        # self.env.filters['escape'] = escape
        # self.env.filters['fmt'] = fmt
        # self.env.filters['xp'] = xp

        # history

        self._populate_interactions()

    @property
    def default_executor(self):
        for stm in self.reactor.inventory.get(DEFAULT_EXECUTOR, {}).values():
            return stm

    async def is_connected(self, timeout=900) -> DefaultExecutor:
        t1 = time.time() + timeout
        while time.time() < t1:
            executor = self.default_executor
            if executor:
                connection = executor.connection
                if connection and connection._host:
                    return executor
            else:
                self.log.debug(f"no executor is defined, exiting...")
                self.push(self.EV_KILL)
                break
            await self.sleep(1)

    def get_interaction(self):
        def lines():
            for line, answer in self.history:
                if answer:
                    line = f"{line} : '{answer}'"
                yield line
            yield self.partial

        return '\n'.join(lines())

    def _term(self, *args, **kw):
        self.cmdline = ''
        self._flush_partial()
        super()._term(*args, **kw)

    def _kill(self, *args, **kw):
        super()._kill(*args, **kw)

    async def _enter_stop(self, *args, **kw):
        self._flush_partial()
        await super()._enter_stop(*args, **kw)

    def _flush_partial(self):
        if self.partial:
            self.history.append((self.partial, '<tail>'))

    # ----------------------------------------------------
    # actions
    # ----------------------------------------------------
    def show_problem(self, action):
        for line in action.history:
            self.log.error(f"{line}")

        self.slowdown()

    def new_action(self, klass: STM, _warm_body=None, **kw):
        # note: we drop 'restart' from kw to be able of creating an instance
        # TODO: block duplicated actions (same action with same **kw)
        # TODO: make self.actions global to all Action instances
        blueprint = list(kw.items())
        blueprint.sort()
        # blueprint = tuple(blueprint)
        blueprint = str(blueprint)
        blueprint = hashlib.sha1(
            bytes(blueprint.encode('utf-8'))
        ).hexdigest()

        key = (klass, blueprint)
        action = self.actions.get(key)
        if not action or (
            action.state in (self.ST_STOP, self.ST_KILL)
            and (time.time() - action.t1)
            > (action.warm_body if _warm_body is None else _warm_body)
        ):
            # action = scall(klass, **kw)
            action = klass(**kw)
            self.reactor.attach(action)
            self.actions[key] = action

        return action

    async def wait_for(
        self, running=None, timeout=60, sleep=0.15, desired_states=None
    ):
        desired_states = desired_states or (self.ST_KILL,)
        if running is None:
            running = list(self.actions.values())

        t0 = time.time()
        t1 = t0 + timeout
        done = []
        last_done, last_running = done, running
        while running and t1 >= t0:
            done = [
                action
                for action in running
                if action.state in desired_states
            ]
            running = [
                action
                for action in running
                if action.state not in desired_states
            ]

            if done != last_done:
                return done, running
            t0 = time.time()
            sleep = min(sleep * 1.2, 2.5, t1 - t0)  # TODO: max = 2
            if sleep > 0:
                await self.sleep(sleep)
                t0 += sleep
            else:
                break

        return done, running

    async def wait(self, *actions, timeout=900, sleep=0.15):
        for action in actions:
            assert (
                action.restart < 0
            ), "Waiting action may not restart (by now)"

        t1 = time.time() + timeout
        actions = list(actions)
        results = []
        while actions:
            for i in range(len(actions) - 1, -1, -1):
                action = actions[i]
                if action.state in (self.ST_KILL,):  # self.ST_STOP):
                    actions.pop(i)
                    # try to get exit status (if aplicable: i.e. Agents
                    # may not have fired a process, just domestic or
                    # sequential tasks)
                    if action.process:
                        try:
                            rc = action.process.exit_status
                        except AttributeError as why:
                            rc = why
                    else:
                        rc = 0

                    if rc > 0:
                        interaction = self.get_interaction()
                        if interaction:
                            self.log.error(f"interaction: {interaction}")
                        else:
                            self.log.info(
                                f"{self.command()} returns ({rc}) without stdout ..."
                            )
                    results.append(rc)

            if actions:
                await self.sleep(sleep)
                if time.time() > t1:
                    msg = f"{actions}: timeout={timeout} secs"
                    self.log.error(msg)
                    # action.push(action.EV_RESTART, restart=5)
                    # self.push(self.EV_RESTART)
                    # t1 += 60  # TODO: select an appropriated value
                    # raise TimeoutError(msg)
                    break
                sleep = min(sleep * 2, 0.5)  # TODO: max = 2
                foo = 1

        #  return action.process.exit_status
        return results

    async def execute(self, *args, **kw):
        """Execute a sequence of commands.
        Abort on 1st error
        """
        stack = inspect.stack()
        context = dict(stack[1].frame.f_locals)
        context.update(**kw)
        context.pop('self')
        # context.pop('template', None)  # TODO: use scall

        for i, cmdline in enumerate(args):
            # cmdline = self.expand(cmdline, **context)
            cmdline = scall(self.expand, cmdline, **context)
            self.log.warning(f"- [{i}]: exec: '{cmdline}'")
            action = self.new_action(
                Action, cmdline=cmdline, sudo=context.get('sudo', True)
            )
            r = await self.wait(action, sleep=0.25)
            if any(r):
                self.log.warning(
                    f"Sequence Execution Failled in task:[{i}] {cmdline}"
                )
                self.log.warning(f"{action.command()}")
                for line in action.history:
                    self.log.warning(f"  {line}")

                return False
        # ok, success
        self.log.warning(f"Sequence of ({i + 1}) tasks Executed Ok")
        return True

    async def create_file(
        self,
        path,
        content=None,
        owner=None,
        group=None,
        mode=None,
        expand=True,
        **ctx,
    ):
        modified = False

        # get the current file attributes
        # TODO: locat dynamically FileFact class

        criteria = {
            'mro()': '.*FileFact.*',
            '__name__': 'FileFact',
        }
        for FileFact in Finder.find_objects(**criteria):
            break
        else:
            raise RuntimeError(f"can't find FileFact class")

        attributes = {}
        _warm_body = None

        async def load_attr():
            nonlocal attributes
            stats = self.new_action(
                FileFact, name=path, _warm_body=_warm_body
            )
            result = await self.wait(stats)

            spec = bspec(stats.prefix, path)
            attributes = self.g(spec, default={})

        if content is not None:
            if expand:
                content = self.expand(content, **ctx)

            temp = temp_filename()
            with open(temp, 'w') as f:
                f.write(content)

            # check if is running in localhost
            executor = await self.is_connected()
            if (
                self.g('hostname') != executor.connection._host
            ):  # localhost != remotehost
                self.log.debug(
                    f"coping file: {temp} to {executor.connection._host}"
                )
                await executor.put(temp, temp)
                os.unlink(temp)
            else:
                self.log.debug(f"Ignoring coping file. Running in localhost")
                foo = 1

            result = await self.execute(
                '{{sudo}} mkdir -p $(dirname "{{ path }}")',
                '{{sudo}} mv --force "{{ temp }}" "{{ path }}"',
                #'{{sudo}} chown {{ owner }}:{{ owner }} "{{ path }}"',
                sudo='sudo -S',
                **ctx,
            )
            _warm_body = 0
            modified = True

        if owner:
            attributes or await load_attr()
            if owner != attributes.get('owner'):
                result = await self.execute(
                    '{{sudo}} chown {{ owner }} "{{ path }}"',
                    sudo='sudo -S',
                    **ctx,
                )
                modified = True

        if group:
            attributes or await load_attr()
            if group != attributes.get('group'):
                result = await self.execute(
                    '{{sudo}} chgrp {{ group }} "{{ path }}"',
                    sudo='sudo -S',
                    **ctx,
                )
                modified = True
        if mode:
            attributes or await load_attr()
            if f"{mode:04}" != attributes.get('mode'):
                # try to move file to final location
                result = await self.execute(
                    '{{sudo}} chmod {{ mode }} "{{ path }}"',
                    sudo='sudo -S',
                    **ctx,
                )
                modified = True

        return modified

    # --------------------------------------------------
    # Interactions
    # --------------------------------------------------
    def add_interaction(self, name, regexps, func=None, **kw):
        if isinstance(regexps, str):
            regexps = [regexps]

        functions = [
            func for func, d in self.find_method(f'(_?interact_)?{func}')
        ]
        self.interactions[name] = (regexps, functions, kw)
        # rebuild dict ordered
        keys = list(self.interactions)
        keys.sort()
        self.interactions = {k: self.interactions[k] for k in keys}
        foo = 1

    def _populate_interactions(self):
        self.add_interaction(
            '999_default-response',
            r'(\[|\()(?P<default>[^/]/[^\]\s]+)(\]|\))',
            'default_response',
        )
        self.add_interaction(
            '900_simple-questions',
            r'(?P<key>[^\s]+)\s+(\[(?P<answer>.*)\]:)',
            'default_response',
            ctx_map={},
        )

        self.add_interaction(
            '100_sudo-nop',
            r'.*sudo.*etc/sudoers.*should\s+be.*(\n|$)',
            ctx_map={},
        )

        self.add_interaction(
            '100_sudo-passwd',
            r'.*sudo.*password\s+for.*:',
            'sudo_passwd',
            ctx_map={},
        )
        # common errors
        self.add_interaction(
            '500_file-not_found',
            r'.*No\s+such\s+file.*directory.*',
            'non_recoverable_error',
            ctx_map={},
        )
        self.add_interaction(
            '500_permission-denied',
            r'.*Permission\denied.*',
            'non_recoverable_error',
            ctx_map={},
        )
        # self.add_interaction(
        #'900_github_username',
        # r'github_username\s+(\[(?P<answer>.*)\]:)',
        #'default_response',
        # ctx_map={
        #'answer': 'github_username',
        # },
        # )
        foo = 1

    def command(self, **kw):
        cmd = self.cmdline
        if cmd:
            # modifiers
            if self.sudo and 'sudo' not in cmd and os.geteuid() != 0:
                cmd = f"sudo -S {cmd}"

            if self.nice:
                cmd = f"nice {cmd}"

            if self.pattern:
                cmd = cmd + " | egrep '{{ pattern }}'"

            # template = self.reactor.env.from_string(cmd)
            # ctx = self.get_ctx(**kw)
            # cmd = template.render(ctx)
            cmd = self.expand(cmd)

        return cmd

    def answer(self, answer):
        stdin = self.process.stdin
        output = f'{answer}\n'
        stdin.write(output)
        self.console(output)

        self.history.append((self.seen, answer))

    async def interact(self):
        """
        Interact with console output:
        - parsing text lines
        - answerig questions from CLI

        You may take in consideration that multiples matches may occurs
        analyzing full console output, so only 1st near match must be
        taken, letting the bigest tail posiible to the next parsing interation.

        """
        last_option = [
            '',  # name,
            0,  # start,
            0,  # end,
            None,  # match,
            [],  # functions,
            {},  # kw,
            r'(?!x)x',  # last_pattern (never match)
        ]
        #  never match

        # is asking something?
        def old_criteria(x):
            name, begin, end = x[:3]
            prefix = name.split('-')[0]
            return prefix, begin, end

        def criteria(x):
            """Sort criteria is:

            - start of text matching
            - end os text matching

            so we preffer who matches first and who matches
            the most, then in even case:

            - the prefix of the rule name: (prefix)-(suffix)
            i.e.: 100_sudo-passwd  --> 100_sudo


            """
            name, begin, end = x[:3]
            prefix = name.split('-')[0]
            return begin, end, prefix

        async def parse():
            nonlocal last_option
            candidates = []

            # explore beginingm tail and full response just to speed up regexp parsing
            for sample in (
                self.partial[: self.reg_depth],
                self.partial[-self.reg_depth :],
                self.partial,
            ):
                # fast match agains last one
                last_pattern = last_option[-1]
                match = re.search(last_pattern, sample)  # self.partial
                match = False  # TODO: disabled, review when attributes still matches new_group
                if match and match.start() == 0:
                    last_option[1:4] = 0, match.end(), match
                    # option = (
                    # name,  # sort will not goes beyind this point
                    # match.start(),
                    # match.end(),
                    # match,  # sort will not goes beyind this point
                    # functions,
                    # kw,
                    # )
                    assert (
                        len(candidates) == 0
                    ), "TODO: reuse already matches from sample"
                    candidates.append(last_option)
                else:
                    # deep search
                    for name, (
                        regexps,
                        functions,
                        kw,
                    ) in self.interactions.items():
                        for pattern in regexps:
                            match = re.search(
                                pattern, sample
                            )  # self.partial)
                            if match:
                                option = [
                                    name,  # sort will not goes beyind this point
                                    match.start(),
                                    match.end(),
                                    match,  # sort will not goes beyind this point
                                    functions,
                                    kw,
                                    pattern,
                                ]
                                candidates.append(option)

                if candidates:
                    # sort candidates
                    candidates.sort(key=criteria)
                    (
                        name,
                        start,
                        end,
                        match,
                        functions,
                        kw,
                        last_pattern,
                    ) = last_option = candidates[0]

                    # TODO: next candidates seems to be valie
                    # TODO: try to reuse and don't make unecessary regexp.searches

                    self.seen = self.partial[:end]
                    self.history.append((self.seen, ''))

                    self.log.debug(f"match: '{name}': {self.seen.strip()}")
                    for func in functions:
                        r = await func(match, **kw)
                    # cut partial response
                    self.partial = self.partial[end:]
                    return True
                elif sample:
                    # we have not matches, but we still have input to parse
                    pass

        i = 0
        result = False
        while self.partial:
            r = await parse()
            if not r:
                break
            result = result or r
            i += 1
            if not (i % 1000):  #  be nice with other tasks
                return True
                # break
                # await self.sleep(0.1)

        return result

    async def _interact_default_response(self, match, **kw):
        # is asking something?
        d = match.groupdict()
        d.update(kw)
        answer = kw.get('answer')
        if answer is None:
            _map = kw.get('ctx_map', {})
            key = d.get('key', 'answer')
            key = _map.get(key, key)
            answer = self.ctx.get(key)
        if answer is None:
            # if re.search(r'\?', self.partial[-20:]):
            question = match.groupdict()['default']
            alternatives = re.findall(r'[^/-]+', question)
            # drop not highligthed
            default = [
                token for token in alternatives if token.lower() != token
            ]
            if default:
                answer = default[-1]
            else:
                answer = alternatives[-1]
        self.answer(f'{answer}')
        foo = 1

    async def _interact_sudo_passwd(self, match, **kw):
        answer = self.default_executor.ctx.get('password')
        if answer:
            self.log.debug(f"provide sudo password: {'*' * len(answer)}")
            self.answer(f'{answer}')
        else:
            self.log.error(f"no sudo password is provided???")

        foo = 1

    async def _interact_non_recoverable_error(self, match, **kw):
        text = match.group(0)
        self.log.error(f"{text}")
        foo = 1

    # --------------------------------------------------
    # Transitions
    # --------------------------------------------------

    def _build_transitions(self):
        super()._build_transitions()
        s = self
        # --------------------------------------------------
        # STM definition
        # --------------------------------------------------

        s.add_transition(s.ST_ANY, s.EV_SUDO, s.ST_SAME)

    # --------------------------------------------------
    # Common transition callbacks
    # --------------------------------------------------
    # Idle
    async def do_Idle(self, *args, **kw):
        """Executed on every idle event, any state"""
        # check for any launched action
        for action in self.actions.values():
            if action.is_active:
                break
        else:
            #  there is another task but main() ?
            for _ in self.my_tasks():
                break
            else:
                self.push(self.EV_TERM)

        await super().do_Idle(*args, **kw)

    async def do_Restart(self, *args, **kw):
        self.log.debug(f"do_Restart: Action '{self}': {args} : {kw}")
        await super().do_Restart(*args, **kw)

    async def _enter_restart(self, *args, **kw):
        self.log.debug(f"_enter_restart: Restarting: '{self}'")
        self.history.clear()
        self.partial = ''
        await super()._enter_restart(*args, **kw)

    async def _enter_ready(self):
        """
        Performs any bootstrap action needed
        """
        # self.log.debug(f"{self.name} is ready!!")
        if self.partial:
            # we can to analyze custom output, no command is not precise
            await super()._enter_ready()
            return

        executor = await self.is_connected()
        if executor:
            self.echo(f"{self.name} default_connection is ready")
            if getattr(executor, 'connection'):
                cmdline = self.command().strip()
                if cmdline:
                    self.process = await executor.create_process(
                        cmdline, stderr=STDOUT
                    )
                    self.log.warning(f">>> Executing: '{cmdline}'")
                    self.log_commands.info(f">>> : '{cmdline}'")
                    await super()._enter_ready()
                else:
                    self.log.debug(
                        f"{self}: No commad line is provided! ..."
                    )
                    # self.slowdown()
                    self.push(self.EV_WAIT)
        else:
            self.log.debug("no default executor found!, kill ...")
            self.push(self.EV_KILL)

    async def _enter_running(self, *args, **kw):
        # TODO: use another strategy to unlock normal flow, instead
        # TODO: block transition in the 'enter' state (it locks 'main' fiber)
        # TODO: i.e. launch a fiber to attend interaction
        # TODO: or use short Idle cycles, etc.
        self.log.debug(
            f"{self.name} is running, interacting with output ..."
        )
        process = self.process
        assert process is not None or self.partial
        # self.response = ''
        # TODO: analyze strerror
        size = 1
        nice_pause = 0.05
        pause = nice_pause
        # There is a problem reading from stdout.
        # if we read and a timeout occurs and the process ends
        # while we are interacting, then, the tail of the stream
        #  if never recived
        # so wee need to guess how many bytes can we read before
        # make the read call
        if process:
            _stdout = process._stdout
            _session = _stdout._session
        max_stream = 1
        while self.running:
            if process:
                size = _session._recv_buf_len
                if size > 0:
                    output = await _stdout.read(size)
                    self.partial += output
                    max_stream = max(len(self.partial), max_stream)

            if self.partial:
                activity = await self.interact()

                if activity:
                    # Action is still interacting with partial
                    pause = nice_pause
                    await self.sleep(nice_pause)

                    self.progress = 1 - len(self.partial) / max_stream
                    self.log.debug(
                        f"{self.name} progress: {100 * self.progress:.2f}%"
                    )
                    continue

            if process and process.exit_status is None:
                # Process is still running, but there's no activity yet

                await self.sleep(self.ctx.get('interact_timeout', pause))
                pause = min(pause * 1.5, 10)

            else:
                # can't interact with partial, and process is dead
                self.partial = self.partial.strip()
                if self.partial:
                    self.log.warning(
                        f"WARN: process ends but ({len(self.partial)}) chars can not been processed: '{self.partial[:80]}' ..."
                    )
                break

        if process:
            self.log.info(
                f"Process '{self.command()}' finished: exit_status: {process.exit_status}, history: {len(self.history)} lines, sending EV_TERM event..."
            )
        else:
            self.log.info(
                f"Process {self} has parsed all input stream: history: {len(self.history)} lines, sending EV_TERM event..."
            )
        self.push(self.EV_TERM)

        foo = 1


#  Example CoockieCutter


class CoockieCutter(Action):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.cmdline = 'cookiecutter https://github.com/audreyfeldroy/cookiecutter-pypackage'
        # default values
        self.ctx['username'] = 'Asterio Gonzalez'
        self.ctx['email'] = 'asterio.gonzalez@gmail.com'
        self.ctx['github_username'] = 'asterio.gonzalez'
        self.ctx['email'] = 'asterio.gonzalez@gmail.com'

        self.ctx['project_name'] = 'swarm IoT'
        self.ctx['project_slug'] = 'swarm_iot'
        self.ctx['project_description'] = 'A nice swarm IoT infrastructure'
        self.ctx['pypi_username'] = 'asteriogonzalez'
        self.ctx['version'] = '0.1.0'
        self.ctx['use_pytest'] = 'y'
        self.ctx['use_black'] = 'y'
        self.ctx['version'] = '0.1.0'

    def _populate_interactions(self):
        super()._populate_interactions()
        self.add_interaction(
            '200_redownload',
            r'Is.*okay.*download.*?(\[(?P<answer>.*)\]:)',
            'default_response',
            answer='yes',
        )
        self.add_interaction(
            '800_simple_questions',
            r'(?P<key>[^\s]+)\s+(\[(?P<answer>.*)\]:)',
            'default_response',
            ctx_map={
                'full_name': 'username',
                'project_short_description': 'project_description',
                #'pypi_username': 'pypi_username',
            },
        )
        # self.add_interaction(
        #'200_full_name',
        # r'full_name\s+(\[(?P<answer>.*)\]:)',
        #'default_response',
        # ctx_map={
        #'answer': 'username',
        # },
        # )

        foo = 1

    def _build_transitions(self):
        super()._build_transitions()
        # --------------------------------------------------
        # STM definition
        # --------------------------------------------------
        s = self

        # s.add_transition(s.ST_READY, s.EV_TERM, s.ST_STOP, s.DO_SAME)
