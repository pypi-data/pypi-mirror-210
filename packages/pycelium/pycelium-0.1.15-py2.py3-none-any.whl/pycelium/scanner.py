#!/usr/bin/env python3
"""
- [ ] set timezone (i.e venoen has GTM+0)
- [ ] unify data from specs, such 'mode', etc

"""
import sys
import os
import time
import random
import re
import hashlib
import yaml
import lzma as xz
import bz2
import gzip

from glom import glom, assign, T

# import paramiko
# from paramiko.client import SSHClient
# from paramiko_expect import SSHClientInteraction

import asyncio, asyncssh, sys

import semver

# sys.path.append(os.path.abspath('.'))

# try:
# print(">> antes")
# import wingdbstub

# print(wingdbstub.__file__)
# print("<< despues")
# except ImportError as why:
# print(f"{why}")

from .tools.mixer import merge_yaml, save_yaml
from .tools.persistence import SORT_PATTERN
from .tools.templating import decode_dict_new_lines, encode_dict_new_lines

from .containers import (
    diff,
    rediff,
    get_deltas,
    new_container,
    simplify,
    xfind,
    walk,
    rebuild,
    option_match,
    gather_values,
)  # , merge


from .definitions import (
    MODEM_FACTS,
    MODEM_FACTS_SUBSET,
    REAL,
    TARGET,
    PKG_FACTS,
    FILE_FACTS,
    SERVICE_FACTS,
    ENV,
    VAR,
)

# TODO: use Shel suppport and use composition instead inheritance for Agent
from .shell import (
    walk,
    rebuild,
    Executor,
    DefaultExecutor,
    Reactor,
    run,
    sleep,
    norm_key,
    norm_val,
    merge,
    bspec,
    Finder,
)

from .packages import DebPkgInstall, PipPkgInstall
from .agent import Agent
from .gathering import *
from .service import (
    HashFileFact,
    FileFact,
    SystemdUnitState,
    SystemUnitStart,
    SystemUnitPath,
)
from .modem import ModemFacts, ModemConfigurator

# from wireguard import WireGuard
# from grafana import Grafana

# ------------------------------------------------
#
# ------------------------------------------------


def compute_uri(ctx):
    """
    blueprint
    {'cpu.processor.0.model_name': 'Intel(R) Celeron(R) CPU  J1900  @ 1.99GHz',
     'cpu.processor.0.microcode': '0x838',
     'cpu.processor.1.model_name': 'Intel(R) Celeron(R) CPU  J1900  @ 1.99GHz',
     'cpu.processor.1.microcode': '0x838',
     'cpu.processor.2.model_name': 'Intel(R) Celeron(R) CPU  J1900  @ 1.99GHz',
     'cpu.processor.2.microcode': '0x838',
     'cpu.processor.3.model_name': 'Intel(R) Celeron(R) CPU  J1900  @ 1.99GHz',
     'cpu.processor.3.microcode': '0x838',
     'ip.lo.mac': '00:00:00:00:00:00',
     'ip.enp1s0.mac': '00:e0:67:0e:2e:ac',
     'ip.enp2s0.mac': '00:e0:67:0e:2e:ad',
     'ip.enp3s0f0.mac': '00:e0:67:0e:2e:ae',
     'ip.enp3s0f1.mac': '00:e0:67:0e:2e:af',
     'ip.docker0.mac': '02:42:4d:4f:e6:ea',
     'ip.veth9b4485c@if9.mac': '02:1f:31:36:f5:d3',
     'ip.veth0c26fbb@if11.mac': '62:64:6d:12:45:d7'}
    """
    keys = [
        "ip\.[^.]+\.mac",
        "cpu\.processor\.\d+\.(model_name|microcode)",
    ]
    blueprint = dict(xfind(ctx, keys))
    # blueprint = json.dumps(blueprint)
    blueprint = yaml.dump(blueprint, Dumper=yaml.Dumper)
    blueprint = hashlib.sha1(blueprint.encode("utf-8")).hexdigest()
    return f"host:{blueprint}"


class SShell(Executor):
    """
    TODO: not used??
    """

    def __init__(
        self,
        hostname,
        username="user",
        password="123456",
        allow_agent=True,
        **kw,
    ):
        super().__init__(**kw)
        self.ctx.update(
            {
                #'hostname': 'wvenoen241',
                #'hostname': 'venoen242',
                "hostname": hostname,
                "username": username,
                "password": password,
                "allow_agent": allow_agent,
            }
        )
        self.executor = SSHClient()
        self.executor.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # self.executor = asyncssh
        # self.executor.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    async def connect(self):
        """
        async def connect(host = '', port: DefTuple[int] = (), *,
                  tunnel: DefTuple[_TunnelConnector] = (),
                  family: DefTuple[int] = (), flags: int = 0,
                  local_addr: DefTuple[HostPort] = (),
                  sock: Optional[socket.socket] = None,
                  config: DefTuple[ConfigPaths] = (),
                  options: Optional[SSHClientConnectionOptions] = None,
                  **kwargs: object) -> SSHClientConnection:
        """
        conn = {
            k: self.ctx.get(k)
            for k in ["hostname", "username", "password", "allow_agent"]
        }
        # ctx = self.ctx
        # conn = {
        #'host': ctx['hostname'],
        # }

        # self.interact = await self.executor.connect(**conn)
        self.interact = self.executor.connect(**conn)
        self.interact = SSHClientInteraction(
            self.executor, timeout=60, display=True
        )

        # change prompt to split console responses
        self.interact.send(
            'export PS1="{prompt}"'.format_map(self.ctx), newline="\r\n"
        )
        r = self.interact.expect(self.ctx["prompt"])
        if r < 0:
            raise RuntimeError(
                f"Can't set custom prompt: {self.ctx['prompt']}"
            )

        self.prompt = self.ctx["prompt"]
        foo = 1

    # def run(self, cmdline, **kw):
    # cmdline = ' '.join(cmd)
    # self.interact.send(cmdline)
    # return stdout

    def run(self, cmdline, *responses, **reactions):
        if self.interact:
            self.interact.send(cmdline)
            response = self.expect(cmdline, **reactions)

        else:
            response = {
                "error": f"{self.__class__.__name__} is not yet connected"
            }

        return response

    def remove_sudo_passwd(self):
        """
        {username} ALL=(ALL:ALL) NOPASSWD:ALL
        """

        reactions = {
            "sudo.*password.*": "sudo_passwd",
        }

        response = self.run("sudo ls -l", **reactions)
        foo = 1

    # def interact(self, cmd, **kw):
    # cmd = cmd.format_map(self.ctx)
    # interact = SSHClientInteraction(
    # self.client, timeout=10, display=True
    # )

    # options = [
    #'sudo.*password.*',
    # ]
    # try:
    # r = interact.send(cmd)
    # r = interact.expect(options, timeout=5)
    # r = interact.send(self.ctx['password'])

    # except Exception as e:
    # print(e.message)

    # err = ''.join(stderr.readlines())
    # out = ''.join(stdout.readlines())
    # return err + out

    def put(self, source, target, **kw):
        scp = self.client.open_sftp()

        scp.put(source.format_map(self.ctx), target.format_map(self.ctx))
        scp.close()


class Old_Settler(Agent):
    """
    An Agent for analyze and configuring a node
    """

    CHANGE_PROMPT = "prompt"
    FIND_SUDO_PASSWD = "sudo_passwd"
    GET_CPU_INFO = "cpu_info"
    GET_DISK_STATS = "disk_stats"
    GET_DEB_PACKAGES = "deb_pkg"
    PKG_DEB_INSTALL = "deb_install"
    GET_PIP_PACKAGES = "pip_pkg"
    PIP_DEB_INSTALL = "pip_install"
    GET_IP_INFO = "ip_info"
    GET_DEVICES = "devices"
    GET_CLASS_INFO = "class_info"
    CLASS_INFO = set(
        [
            "bios_vendor",
            "board_name",
            "product_uuid",
        ]
    )
    GET_ETC_INFO = "etc_info"
    ETC_INFO = set(
        [
            "machine-id",
        ]
    )

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)

        self.grains = {}

    def _build_transitions(self):
        super()._build_transitions()
        # --------------------------------------------------
        # STM definition
        # --------------------------------------------------
        s = self

        self.add_transition("boot", "None", "boot", "boot")
        self.add_transition("boot", "ready", "real")

        self.add_transition("real", "None", "real", "real")
        self.add_transition("real", "ready", "analyze")

        self.add_transition("analyze", "None", "analyze", "analyze")
        self.add_transition("analyze", "ready", "configure")
        self.add_transition("analyze", "stop", "stop")

        self.add_transition("configure", "None", "configure", "configure")
        self.add_transition("configure", "ready", "stop")

        # gather info from host no matter what
        self.add_transition(".*", "get_cpu", self.ST_SAME, "get_cpu")
        self.add_transition(".*", "get_ip", self.ST_SAME, "get_ip")
        self.add_transition(".*", "get_disk", self.ST_SAME, "get_disk")
        self.add_transition(".*", "deb_pkg", self.ST_SAME, "deb_pkg")
        self.add_transition(".*", "deb_install", self.ST_SAME, "deb_install")
        self.add_transition(".*", "pip_pkg", self.ST_SAME, "pip_pkg")
        self.add_transition(".*", "pip_install", self.ST_SAME, "pip_install")
        self.add_transition(".*", "get_devices", self.ST_SAME, "get_devices")
        self.add_transition(
            ".*", "get_class_info", self.ST_SAME, "get_class_info"
        )
        self.add_transition(
            ".*", "get_etc_info", self.ST_SAME, "get_etc_info"
        )
        self.add_transition("idle", "None", "idle", "idle")

    async def do_boot(self):
        """
        Performs any bootstrap action needed
        """
        self.echo(f"{self.name} is booting!!")
        executor = self.executor.executor
        if executor is None:
            await self.queue.put(self.EV_CONNECT)

        if executor and True:  # example of multiple conditions
            await self.queue.put(self.EV_READY)

    async def do_connect(self):
        """
        Try to connect to host
        """
        self.echo(f"{self.name} connecting")
        await self.executor.connect()

    async def do_facts(self):
        """
        Try to get any missing needed fact before analyze node
        """
        cpu = self.ctx.get("cpu")
        if not cpu:
            await self.queue.put("get_cpu")
        ip = self.ctx.get("ip")
        if not ip:
            await self.queue.put("get_ip")
        disk = self.ctx.get("disk")
        if not disk:
            await self.queue.put("get_disk")

        deb_pkg = self.ctx.get("deb_pkg")
        if not deb_pkg:
            await self.queue.put("deb_pkg")

        pip_pkg = self.ctx.get("pip_pkg")
        if not pip_pkg:
            await self.queue.put("pip_pkg")

        devices = self.ctx.get("devices")
        if not devices:
            await self.queue.put("get_devices")

        class_info = set(self.ctx.get("class_info", {}))
        if class_info != self.CLASS_INFO:
            await self.queue.put("get_class_info")

        etc_info = set(self.ctx.get("etc_info", {}))
        if etc_info != self.ETC_INFO:
            await self.queue.put("get_etc_info")

        # TODO: check if this node match any targeted groups
        if (
            cpu
            and ip
            and disk
            and deb_pkg
            and pip_pkg
            and devices
            and class_info == self.CLASS_INFO
        ):
            self.ctx["uri"] = compute_uri(self.ctx)
            await self.queue.put("ready")

    async def do_get_cpu(self):
        self.echo(f"{self.name} get_cpu")
        response = await self.collect(self.GET_CPU_INFO, split_lines=True)
        foo = 1

    async def do_get_ip(self):
        self.echo(f"{self.name} get_ip")
        response = self.collect(self.GET_IP_INFO, split_lines=True)
        foo = 1

    async def do_get_devices(self):
        self.echo(f"{self.name} get_devices")
        response = self.collect(self.GET_DEVICES, split_lines=True)
        foo = 1

    async def do_get_disk(self):
        self.echo(f"{self.name} get_disk")
        response = self.collect(self.GET_DISK_STATS, split_lines=True)
        foo = 1

    async def do_deb_pkg(self):
        self.echo(f"{self.name} deb_pkg")
        response = self.collect(self.GET_DEB_PACKAGES, split_lines=True)
        foo = 1

    async def do_pip_pkg(self):
        self.echo(f"{self.name} pip_pkg")
        response = self.collect(self.GET_PIP_PACKAGES, split_lines=True)
        foo = 1

    async def do_deb_install(self):
        self.echo(f"{self.name} deb_install")
        response = self.collect(
            self.PKG_DEB_INSTALL, split_lines=False, name="python3-selenium"
        )
        foo = 1

    async def do_pip_install(self):
        self.echo(f"{self.name} pip_install")
        response = self.collect(self.PKG_PIP_INSTALL, split_lines=False)
        foo = 1

    async def do_get_class_info(self):
        """
        /sys/class/dmi/id/product_uuid
        03000200-0400-0500-0006-000700080009
        """
        self.echo(f"{self.name} get_class_info")
        class_info = self.ctx.setdefault("class_info", {})
        for name in self.CLASS_INFO.difference(class_info):
            response = self.collect(self.GET_CLASS_INFO, name=name)
            value = response.get("last")
            if value is not None:
                class_info[name] = value
            foo = 1

    async def do_get_etc_info(self):
        etc_info = self.ctx.setdefault("etc_info", {})
        for name in self.ETC_INFO.difference(etc_info):
            response = self.collect(self.GET_ETC_INFO, name=name)
            value = response.get("last")
            if value is not None:
                etc_info[name] = value
                foo = 1

    async def do_analyze(self):
        self.echo(f"{self.name} is analyzing!!")
        # self.ctx['sleep'] = 1.0
        # TODO: move to yaml config file (use list instead tuples by yaml definition :) )
        blueprint = [
            [
                "class_info\.board_name",
                "Aptio\s+CRB$",
            ],
            [
                "class_info\.product_uuid",
                "03000200-0400-0500-0006-000700080009",
            ],
            [
                "class_info\.bios_vendor",
                "American\s+Megatrends.*",
            ],
            [
                "class_info\.product_uuid",
                "03000200-0400-0500-0006-000700080009",
            ],
        ]
        blueprint = [
            [
                "class_info\.board_name",
                ".*",
            ],
            [
                "class_info\.product_uuid",
                ".*",
            ],
            [
                "class_info\.bios_vendor",
                ".*",
            ],
            [
                "class_info\.product_uuid",
                ".*",
            ],
        ]
        candidates = []
        for key, value in walk(self.ctx):
            key = ".".join(key)
            value = str(value)
            print(f"{key}: {value}")

            for kpattern, vpattern in blueprint:
                if re.match(kpattern, key):
                    candidates.append(re.match(vpattern, value) is not None)

            foo = 1

        if not candidates or all(candidates):
            await self.queue.put("ready")
        else:
            foo = 1

    async def do_configure(self):
        self.echo(f"{self.name} is configuring!!")

        # self.ctx['sleep'] = 5.0
        if True:
            await self.queue.put("deb_install")  # , name='python3-selenium')
            await self.queue.put("ready")

    async def do_idle(self):
        self.echo(f"{self.name} is idle!!")
        self.ctx["sleep"] = 5.0

    async def do_stop(self):
        self.echo(f"{self.name} is stopping!!")
        self.running = False

    # async def do_state_any_connected_false(self, **kw):
    # self.echo(f"{self.name} connecting remote host:")
    # self.ctx.pop('connected')
    # self.shell.connect()

    # async def do_state_idle(self, **kw):
    # self.echo(f"{self.name} is idle !!")
    # if random.random() < 0.35:
    # await self.stop()

    # async def do_state_idle_sudo_passwd_none_connected_true(self, **kw):
    # self.echo(f"{self.name} has no sudo passwd:")

    # cmdline = """
    # sudo echo "%user ALL=(ALL:ALL) NOPASSWD:ALL" | sudo tee /etc/sudoers.d/user_nopasswd
    # """
    # r = self.shell.run(cmdline)
    # foo = 1

    @property
    def sudo_passwd(self):
        response = self.collect(self.FIND_SUDO_PASSWD)
        # interact = self.shell.interact
        # interact.send(
        #'export PS1="{prompt}"'.format_map(self.ctx), newline='\r\n'
        # )
        # r = interact.expect(self.ctx['prompt'])
        # if r < 0:
        # raise RuntimeError(
        # f"Can't set custom prompt: {self.ctx['prompt']}"
        # )

        return False

    @property
    def connected(self):
        return self.executor.interact is not None

    def _populate_patterns(self):
        super()._populate_patterns()
        # -------------------------------------------------
        # CHANGE_PROMPT
        # -------------------------------------------------
        self.add(
            self.CHANGE_PROMPT,
            'export PS1="{{ prompt }}"',
            [
                (
                    "prompt",
                    """(?imsux)
                    /(?P<sudo_passwd>.*_nopasswd)$
                    """,
                    {},
                ),
            ],
            False,
        )
        # -------------------------------------------------
        # GET_CPU_INFO
        # -------------------------------------------------
        self.add(
            self.GET_CPU_INFO,
            "cat /proc/cpuinfo",
            [
                (
                    "cpu",
                    r"""(?imsx)
                       \s*
                       (?P<_idx_1>processor)
                       [\s:]*\s+
                       (?P<_idx_2>.+?)
                       \s*$
                    """,
                    {},
                ),
                (
                    "cpu",
                    r"""(?imsx)
                       \s*
                       (?P<_key_3>[^:]+)
                       [:]*\s+
                       (?P<_value_>.+?)
                       \s*$
                    """,
                    {},
                ),
            ],
            False,
        )
        # -------------------------------------------------
        # GET_DISK_STATS
        # -------------------------------------------------
        self.add(
            self.GET_DISK_STATS,
            "cat /proc/diskstats",
            [
                (
                    "disk",
                    r"""(?imsx)
                       \s*
                       \d+\s+\d+\s+
                       (?P<_key_1>[^\s]+)\s+
                       (?P<_value_>[\s\d]+)
                    """,
                    {},
                ),
            ],
            False,
        )
        # -------------------------------------------------
        # GET_DEB_PACKAGES
        # -------------------------------------------------
        self.add(
            self.GET_DEB_PACKAGES,
            "dpkg --get-selections",
            [
                (
                    "deb_pkg",
                    r"""(?imsx)
                       \s*
                       (?P<_key_1>[^\s]+)\s+
                       (?P<_value_>[^\s]+)
                    """,
                    {},
                ),
            ],
            False,
        )
        # -------------------------------------------------
        # GET_PIP_PACKAGES
        # -------------------------------------------------
        self.add(
            self.GET_PIP_PACKAGES,
            "pip list",
            [
                # Package Version Editable project location
                # ------ -------- --------------------------
                (
                    "pip_pkg",
                    r"""(?imsx)
                       \s*
                       Package\s+Version\s+
                       .*?
                       $
                    """,
                    {},
                ),
                (
                    "pip_pkg",
                    r"""(?imsx)
                   \s*
                   [-\s]+
                   $
                   """,
                    {},
                ),
                (
                    "pip_pkg",
                    r"""(?imsx)
                       \s*
                       (?P<_key_1>[^\s]+)\s+
                       (?P<_value_>[^\s]+)
                       (\s+(?P<_path_>[^\s]+))?
                       .*$
                    """,
                    {},
                ),
            ],
            False,
        )
        # -------------------------------------------------
        # GET_IP_INFO
        # -------------------------------------------------
        self.add(
            self.GET_IP_INFO,
            "ip a",
            [
                (
                    "ip",
                    r"""(?imsx)
                       \s*
                       (\d+):\s+
                       (?P<_idx_1>lo|enp\d+|wg\d+|docker\d+|veth\d+|wwan\d+[^:]*):
                    """,
                    {},
                ),
                (
                    "ip",
                    r"""(?msx)
                       \s*
                       (?P<_key_2>mtu)\s+
                       (?P<_value_>\d+)
                    """,
                    {},
                ),
                (
                    "ip",
                    r"""(?msx)
                       \s*
                       (?P<_key_2>state)\s+
                       (?P<_value_>UNKNOWN|DOWN|UP)
                    """,
                    {},
                ),
                (
                    "ip",
                    r"""(?msx)
                       \s*
                       (?P<_key_2>link)/
                       (?P<_value_>loopback|ether)\s+
                       (?P<__mac__>[0-9a-f:]+)
                    """,
                    {},
                ),
                # no mac address (i.e WG)
                (
                    "ip",
                    r"""(?msx)
                       \s*
                       (?P<_key_2>link)/
                       (?P<_value_>none)
                    """,
                    {},
                ),
                (
                    "ip",
                    r"""(?msx)
                       \s*
                       (?P<_key_2>inet)\s+
                       (?P<_value_>\d+\.\d+\.\d+\.\d+/\d+)\s
                    """,
                    {},
                ),
            ],
            False,
        )
        # -------------------------------------------------
        # GET_DEVICES
        # -------------------------------------------------
        self.add(
            self.GET_DEVICES,
            "cat /proc/devices",
            [
                (
                    "devices",
                    r"""(?imsx)
                       \s*
                       (?P<_idx_1>character|block)\s+devices:
                    """,
                    {},
                ),
                (
                    "devices",
                    r"""(?msx)
                       \s*
                       (?P<_key_2>\d+)\s+
                       (?P<_value_>[^s]+)
                       \s*
                    """,
                    {},
                ),
            ],
            False,
        )

        # -------------------------------------------------
        # GET_CLASS
        # -------------------------------------------------
        self.add(
            self.GET_CLASS_INFO,
            "sudo cat /sys/class/dmi/id/{{ name }}",
            [
                (
                    "last",
                    r"""(?imsux)
                    (?P<_value_>.*)
                    $
                    """,
                    {},
                ),
            ],
            False,
        )
        # -------------------------------------------------
        # GET_ETC_INFO
        # -------------------------------------------------
        self.add(
            self.GET_ETC_INFO,
            "sudo cat /etc/{{ name }}",
            [
                (
                    "last",
                    r"""(?imsux)
                    (?P<_value_>.*)
                    $
                    """,
                    {},
                ),
            ],
            False,
        )
        # -------------------------------------------------
        # FIND_SUDO_PASSWD
        # -------------------------------------------------
        self.add(
            self.FIND_SUDO_PASSWD,
            "sudo ls /etc/sudoers.d/{{ username }}_nopasswd",
            [
                (
                    "sudo_passwd",
                    """(?imsux)
                    /(?P<sudo_passwd>.*_nopasswd)$
                    """,
                    {},
                ),
                (
                    "sudo_no_passwd",
                    """(?imsux)
                    /(?P<sudo_passwd>.*No\s+such\s+file.*)$
                    """,
                    {},
                ),
            ],
            False,
        )
        # -------------------------------------------------
        # DEB_INSTALL
        # -------------------------------------------------
        self.add(
            self.PKG_DEB_INSTALL,
            "sudo apt install -y {{ name }}",
            [
                # xxxx is already the newest version
                (
                    "deb_install",
                    r"""(?imsx)
                       \s*
                       (?P<__deb_installed__>{{ name }})
                       \sis\s+already\s+the\s+newest\s+version
                    """,
                    {},
                ),
                # The following additional packages will be installed:
                (
                    "deb_install",
                    r"""(?msx)
                       \s*
                       The\s+following\s+NEW\s+packages\swill\s+be\s+installed\s+
                       (?P<__deb_installed__>{{ name }})
                       \s+
                       .*?
                       Setting\s+up\s+
                       ({{ name }})
                       .*
                       $
                    """,
                    {},
                ),
                # 7fProgress
                (
                    "deb_install",
                    r"""(?msx)
                       \s*
                       Progress:
                       .*?\n
                    """,
                    {},
                ),
            ],
            False,
        )

        # -------------------------------------------------
        # LIST_FILES (not used by now)
        # -------------------------------------------------
        self.add(
            "list_files",
            "ls -l",
            [
                (
                    "total",
                    """(?msx)
                    total\s+
                    (?P<number>\d+)
                    """,
                    {},
                ),
                (
                    "file",
                    """(?msx)
                    .*?
                    (?P<script>\w+\.sh$)
                    """,
                    {},
                ),
            ],
        )


ENABLE_STATUS = (
    'start',
    'started',
    'restart',
    'restarted',
    'enable',
    'yes',
    'active',
)


class HostInventory(Agent):
    def __init__(self, daemon=True, *args, **kw):
        super().__init__(*args, **kw)
        self.daemon = daemon
        self.action_patterns = {}

    # --------------------------------------------------
    # Bootstraping
    # --------------------------------------------------
    async def _boot_sentinels(self, *args, **kw):
        """
        Domestic fiber for gathering system info.
        """
        # TODO: load from yaml file
        real = [
            {
                "klass": CPUInfoFact,
            },
            {
                "klass": DeviceInfoFact,
            },
            {
                "klass": DiskInfoFact,
            },
            {
                "klass": IPInfoFact,
            },
        ]

        # initial launch
        for action in real:
            self.log.debug(f"Launching: {action}")
            if "klass" in action:
                if self.daemon:
                    action["restart"] = -1  # will not restart
                self.new_action(**action)
                await self.sleep(0.50)

        self.log.debug(f"All bootstrap ({len(real)}) actions fired.")

        foo = 1


class Settler(Agent):
    def __init__(self, specs='specs', daemon=True, *args, **kw):
        super().__init__(*args, **kw)
        self.specs = specs
        self.daemon = daemon
        self.action_patterns = {}

    # async def _do_Idle_ready_ready(self, *args, **kw):
    async def do_Idle(self, *args, **kw):
        self.log.info("Reloading desired target state...")
        spec = bspec(TARGET)
        current = self.g(spec)

        env = dict(self.g(ENV))
        env['folders'] = [
            os.path.join(p, self.specs) for p in env.get('folders')
        ]

        target = merge_yaml(sort_pattern=SORT_PATTERN, **env)
        decode_dict_new_lines(target)
        if str(current) != str(target):
            self.log.warning("ok, target state has changed. Applying...")
            self.s(spec, target)
            ctx = dict(self.g('env'))
            ctx.update(self.reactor.ctx)
            path = self.expand("output/{{ observed_hostname }}.yaml", **ctx)
            # encode_dict_new_lines(target)  # NO!
            save_yaml(target, path)
        else:
            self.log.debug("target state unchanged")
        await super().do_Idle(*args, **kw)
        foo = 1

    # --------------------------------------------------
    # Bootstraping
    # --------------------------------------------------
    async def _boot_sentinels(self, *args, **kw):
        """
        Domestic fiber for gathering system info.
        """
        # TODO: load from yaml file
        real = [
            {
                # "klass": CPUInfoFact,
                "restart": -1,
            },
            {
                # "klass": DeviceInfoFact,
            },
            {
                # "klass": DiskInfoFact,
            },
            {
                # "klass": IPInfoFact,
            },
            {
                # "klass": PipListFact,
                "upgradable": True,
            },
            {
                # "klass": DebListFact,
                'merge': False,
            },
            {
                # "klass": DebAvailableFact,
                'merge': False,
            },
            {
                #'klass': PipListFact,
            },
            {
                #'klass': AddSudoers,
            },
            {
                #'klass': ChangeLocale,
            },
            {
                #'klass': Service,
                #'service_name': 'grafana',
                #'restart': 5,
            },
            {
                "klass": ModemConfigurator,
                # "restart": 300,
            },
            {
                # "klass": DebRepoFact,
            }
            # {
            #'klass': Service,
            #'service_name': 'wireguard',
            #'restart': 5,
            # },
        ]

        # initial launch
        for action in real:
            self.log.debug(f"Launching: {action}")
            if "klass" in action:
                if self.daemon:
                    action["restart"] = -1  # will not restart
                self.new_action(**action)
                await self.sleep(0.25)

        self.log.info(f"All bootstrap ({len(real)}) actions fired.")

        foo = 1

    # --------------------------------------------------
    # Domestic Fibers
    # --------------------------------------------------

    async def _fiber_sentinel(self, *args, **kw):
        """
        'var', 'net', 'modem', '.*',              'connection_name'), None ---> gsm-connection
        'var', 'net', 'modem', '865847056968900', 'connection_name'), None ---> gsm-connection


        """
        # wait until running bootstrap fibers has done/restarted
        pending = None
        while False and self.running:  # TODO: review, may create a dead-lock
            #  wai for gather actions to be finish for 1st time
            done, pending = await self.wait_for(
                pending,
                timeout=300,
                desired_states=(
                    self.ST_KILL,
                    self.ST_RESTART,
                    self.ST_RUNNING,
                ),
            )
            if pending:
                self.log.warning(
                    f"[{pending}] are taking too much time to complete ... retry"
                )
            else:
                self.log.info(f"1st information gathering complete!")
                break

        # compute differencial state and try to close the GAP
        while self.running:
            target = self.g(TARGET)
            if target is None:
                self.log.warning(
                    f"No target state is defined yet. Retry later..."
                )
                self.slowdown()
                await self.sleep()
                continue

            real = self.g(REAL, default={})

            # result0 = diff(target, real, mode="dict")

            result = rediff(target, real, mode="dict")

            result = [d for d in get_deltas(result) if d[0][:1] in (VAR,)]
            # result = list(get_deltas(result))

            result.sort(key=precedence)

            self.log.debug(f"Found {len(result)} deltas")

            # TODO: remove hack
            if len(result) == 2:
                result.clear()

            if not result:
                self.log.warning(f"No deltas found")
                if self.daemon:
                    self.slowdown()
                    self.log.info(f"Sleeping for {self.ctx.get('sleep')}")
                    await self.sleep()
                    continue
                else:
                    self.log.info(f"daemon flag is not set. Stopping {self}")
                    break

            for i, delta in enumerate(result):
                key, old, new = delta
                self.log.debug(f"[{i}]: {key}, {old} ---> {new}")

            foo = 1

            def more():
                # last_key = tuple()
                for i, delta in enumerate(result):
                    key, old, new = delta

                    coros = self._guess_coros(delta)
                    self.log.info(
                        f"Guessing: [{i}]: {key}, {old} ---> {new} : {coros}"
                    )
                    yield coros

            # TODO: experiment. Run all GAP coros in parallel (idempotent)
            max_coros = 10
            running = set()

            async def _wait():
                nonlocal running
                done, running = await asyncio.wait(
                    running,
                    return_when=asyncio.FIRST_COMPLETED,
                )

            foo = 1
            for coros in more():
                if not coros:
                    await self.sleep()
                    continue
                running.update(coros)
                while len(running) >= max_coros:
                    await _wait()

            while running:
                await _wait()

            foo = 1

            await self.sleep()
            foo = 1
        self.hurryup('.*')

    def _guess_coros(self, delta, *args, **kw):
        key, old, new = delta
        path = '_'.join(key)
        coros = self._get_coros('gap', path, delta=delta)
        return coros

    async def old_guess_action(self, delta, *args, **kw):
        key, old, new = delta
        path = '_'.join(key)
        result = await self.dispatch('gap', path, delta=delta)
        foo = 1

    # --------------------------------------------------
    # fs
    # --------------------------------------------------
    async def _gap_var_fs_any_content(self, delta, *args, **kw):
        """
        ('var', 'fs', '/etc/wireguard/wg0.conf', 'content')
        None
        <content ...>
        """
        key, old, new = delta
        path = key[2]
        self.log.debug(f"GAP: Resolving: {delta}")
        remote = self.new_action(HashFileFact, name=path)
        result = await self.wait(remote)

        remote_hash = self.g(remote.prefix, path, 'sha1')  # or None

        local_hash = hashlib.sha1(bytes(new.encode('utf-8'))).hexdigest()

        if remote_hash != local_hash:
            self.log.info(
                f"Updating file: {new}. Hash differs: local: {local_hash}, remote: {remote_hash}"
            )

            # get the current file attributes
            attributes = self.new_action(FileFact, name=path)
            result = await self.wait(attributes)

            attributes = self.g(
                attributes.prefix, path, default={}
            )  # or None

            await self.create_file(path, content=new, **attributes)

            foo = 1
        else:
            self.log.debug(f"Contents for '{path}' is unchanged. Skip.")
            spec = bspec(REAL, key)
            self.s(spec, new)

            foo = 1

        await self.sleep()
        foo = 1

    async def _gap_var_fs_contains(self, delta, *args, **kw):
        self.log.debug(f"GAP: Resolving: {args}: {kw}")
        await self.sleep()
        foo = 1

    async def _gap_var_fs_any_owner(self, delta, *args, **kw):
        """
        ('var', 'fs', '/etc/wireguard/wg0.conf', 'content')
        None
        <content ...>
        """
        key, old, new = delta
        path = key[2]
        self.log.debug(f"GAP: Resolving: {args}: {kw}")
        result = await self.create_file(path, owner=new)

        await self.sleep()
        foo = 1

    async def _gap_var_fs_any_group(self, delta, *args, **kw):
        """
        ('var', 'fs', '/etc/wireguard/wg0.conf', 'content')
        None
        <content ...>
        """
        key, old, new = delta
        path = key[2]
        self.log.debug(f"GAP: Resolving: {args}: {kw}")
        result = await self.create_file(path, group=new)

        await self.sleep()
        foo = 1

    async def _gap_var_fs_any_mode(self, delta, *args, **kw):
        """
        ('var', 'fs', '/etc/wireguard/wg0.conf', 'content')
        None
        <content ...>
        """
        key, old, new = delta
        path = key[2]
        self.log.debug(f"GAP: Resolving: {args}: {kw}")
        result = await self.create_file(path, mode=new)

        # await self.sleep()
        foo = 1

    # --------------------------------------------------
    # services
    # --------------------------------------------------

    async def _gap_var_services_any_status_any(self, delta, *args, **kw):
        self.log.debug(f"GAP: Resolving: {delta}")

        key, old, new = delta
        name = key[2]
        enable = new in ENABLE_STATUS

        service = self.new_action(SystemUnitStart, name=name, enable=enable)
        await self.wait(service)
        foo = 1

    async def _gap_var_services_any_restart_any(self, delta, *args, **kw):
        """
        - enable service if it was missing
        - Create .path unit
        - Create restart.service
        - enable --now .path unit
        """
        self.log.debug(f"GAP: Resolving: {delta}")

        key, old, new = delta  # TODO: review!!
        new = new.lower()

        name = key[2]
        enable = False

        enable = new in ENABLE_STATUS

        service = self.new_action(SystemdUnitState, name=name, enable=enable)
        await self.wait(service)
        foo = 1

    async def _gap_var_services_any_watch_any(self, delta, *args, **kw):
        """
        - enable service if it was missing
        - Create .path unit
        - Create restart.service
        - enable --now .path unit
        """
        self.log.debug(f"GAP: Resolving: {delta}")

        key, old, new = delta
        new = new.lower()

        name = key[2]
        watch = key[3]
        if watch in (SystemUnitPath.MONITOR_KEYWORD,):
            path = key[4]
            enable = new in ENABLE_STATUS
            service = self.new_action(
                SystemUnitPath, name=name, enable=enable, path=path
            )
            result = await self.wait(service)
            if not result:
                self.log.warning(f"timeout waiting: {service}")
        else:
            self.log.error("Function can't find .path unit")

        foo = 1

    # --------------------------------------------------
    # packages
    # --------------------------------------------------
    async def _gap_etc_repository_deb(self, delta, *args, **kw):
        path, old, new = delta
        name = path[-1]

        await self.sleep(1)

    async def _gap_var_pkg_deb(self, delta, *args, **kw):
        path, old, new = delta
        name = path[-1]

        self.log.debug(f"GAP: Resolving: {path}: {old} --> {new}")

        need_uninstall = False
        need_install = False

        installed = self.new_action(DebListFact, pattern=name, _warm_body=0)
        await self.wait(installed)
        status = self.g(installed.prefix)
        status = status and status.get(name)

        # direct uninstall
        if new in (
            'uninstall',
            'remove',
            'delete',
        ):
            if status in ('install',):
                need_uninstall = True
                self.log.info(f"Uninstalling Package '{name}'")
            else:
                self.log.info(
                    f"Package '{name}' is not installed. Do not remove it."
                )

        # downgrade
        if False:  # TODO: review
            need_uninstall = True

        # direct install
        if new in ('install',):
            if status not in ('install',):
                self.log.info(
                    f"Installing Package '{name}' to lastest version"
                )
                need_install = True
            else:
                self.log.info(
                    f"Package '{name}' is already installed and desired version {new} != lastest"
                )

        # upgrade?
        if new in ('lastest',):
            if status in ('install',):
                # check only known packages that are upgradables
                upgrade = self.new_action(
                    DebAvailableFact,
                    pattern=name,
                    upgradable=True,
                    merge=False,
                    _warm_body=0,
                )
                await self.wait(upgrade)
                status = self.g(upgrade.prefix, _target_=upgrade.facts)
                if status and status.get(name):
                    # can be upgraded
                    info = status[name]
                    self.log.info(
                        f"Upgrading {name} from '{info.get('old_version')}' --> '{info.get('version')}' version"
                    )
                    need_install = True
                else:
                    self.log.info(
                        f"{name} is installed and is the lastest available version"
                    )
                    spec = bspec(DEB_FACTS, name)
                    self.s(spec, new)
                    foo = 1
            else:
                self.log.info(
                    f"Installing Package '{name}' to lastest version"
                )
                need_install = True

        if need_uninstall:
            install = self.new_action(
                DebPkgInstall, name=name, install=False
            )
            result = await self.wait(install)
            if not any(result):
                self.log.info(f"Package '{name}' uninstalled successfully")
            else:
                self.log.error(f"Package '{name}' could not be uninstalled!")
                self.log.error(self.get_interaction())
            foo = 1

        if need_install:
            install = self.new_action(DebPkgInstall, name=name)
            result = await self.wait(install)
            if not any(result):
                self.log.info(f"Package '{name}' installed successfully")
            else:
                self.log.error(f"Package '{name}' could not be installed!")
                self.log.error(self.get_interaction())
            foo = 1

        # await self.sleep()  # TODO: remove?
        foo = 1

    async def _gap_var_pkg_pip(self, delta, *args, **kw):
        # check for python3-pip existence
        name = 'python3-pip'
        installed = self.new_action(
            DebListFact, pattern=name, _warm_body=900
        )
        await self.wait(installed)
        status = self.g(installed.prefix)
        status = status and status.get(name)
        if not status:
            install = self.new_action(DebPkgInstall, name=name)
            result = await self.wait(install)
            if any(result):
                return False

        path, old, new = delta
        name = path[-1]

        self.log.debug(f"GAP: Resolving: {path}: {old} --> {new}")

        need_uninstall = False
        need_install = False

        installed = self.new_action(PipListFact, upgradable=False)
        result = await self.wait(installed)  # 0: ok, 1: not found
        status = self.g(installed.prefix, name, default={})
        # status ={'aversion': '2023.3', 'cversion': '2022.1', 'path': '', 'type': 'wheel'}

        # direct uninstall
        if new in (
            'uninstall',
            'remove',
            'delete',
        ):
            if status in ('install',):
                need_uninstall = True
                self.log.info(f"Uninstalling Package '{name}'")
            else:
                self.log.info(
                    f"Package '{name}' is not installed. Do not remove it."
                )

        # downgrade
        if False:  # TODO: review
            need_uninstall = True

        # direct install
        current_version = status.get('cversion')
        if new in ('install',):
            if not current_version:
                self.log.info(
                    f"Installing Package '{name}' to lastest version"
                )
                need_install = True
            else:
                self.log.info(
                    f"Package '{name}' is already installed with version {current_version}, and status: {new} != lastest"
                )

        # upgrade?
        if new in ('lastest',):
            if not 'aversion' in status:
                # get updateable packages only
                upgrade = self.new_action(
                    PipListFact, upgradable=True, _warm_body=600
                )
                result = await self.wait(upgrade)  # 0: ok, 1: not found
                status = self.g(installed.prefix, name, default={})

            available_version = status.get('aversion')
            if not status or (
                available_version
                and current_version
                and available_version != current_version
            ):
                # can be upgraded
                self.log.info(
                    f"Upgrading {name} from '{current_version}' --> '{available_version}' version"
                )
                need_install = True
                # need_uninstall = True
            else:
                self.log.info(
                    f"Installing Package '{name}' to lastest version"
                )
                need_install = False

        if need_uninstall:
            install = self.new_action(
                PipPkgInstall, name=name, install=False, _warm_body=60
            )
            result = await self.wait(install)
            if not any(result):
                self.log.info(f"Package '{name}' uninstalled successfully")
            else:
                self.log.error(f"Package '{name}' could not be uninstalled!")
                self.log.error(self.get_interaction())
            foo = 1

        if need_install:
            install = self.new_action(PipPkgInstall, name=name)
            result = await self.wait(install)
            if not any(result):
                self.log.info(f"Package '{name}' installed successfully")
                check = self.new_action(PipListFact, upgradable=False)
                result = await self.wait(check)  # 0: ok, 1: not found
                status = self.g(installed.prefix, name, default={})
                assert status.get('aversion') in (
                    status.get('cversion'),
                    None,
                )
            else:
                self.log.error(f"Package '{name}' could not be installed!")
                self.log.error(self.get_interaction())
            foo = 1

        # await self.sleep()  # TODO: remove?
        foo = 1

    # --------------------------------------------------
    # modem
    # --------------------------------------------------
    async def _gap_var_net_modem_any_status_state(self, delta, *args, **kw):
        """
        'var', 'net', 'modem', '.*', 'status', 'state'

        state: ['disabled', 'enabling', 'enabled', 'connected', 'disconnected']
        """
        self.log.debug(f"GAP: Resolving: {delta}")

        key, old, new = delta

        #  search modem_id in a more resilian way than direct searh
        # spec = bspec(REAL, key[:4], 'general', 'modem_id')
        # modem_id = self.g(spec, default=None)
        modem_uid = key[3]

        enable = option_match(new, 'ena.*', 'con.*')
        enable = enable is not None
        name = f"ModemConfigurator_modem_id_{modem_uid}"

        modem = self.new_action(
            ModemConfigurator, enable=enable, prefix=REAL + key[:4]
        )
        await self.wait(modem)
        foo = 1

    async def hide_gap_var_net_modem_any_status_power_state(
        self, delta, *args, **kw
    ):
        """
        'var', 'net', 'modem', '.*', 'status', 'power_state'
        """
        self.log.debug(f"GAP: Resolving: {delta}")

        key, old, new = delta
        modem_uuid = key[3]
        status = new in ENABLE_STATUS

        service = self.new_action(SystemUnitStart, name=name, enable=enable)
        await self.wait(service)
        foo = 1


# heuristic delta sorting
PRECEDENCE = {
    PKG_FACTS: 1000,
    FILE_FACTS: 2000,
    SERVICE_FACTS: 3000,
}


def precedence(x):
    key = x[0]
    sub = key[:2]
    score = PRECEDENCE.get(sub, 4000)
    if len(key) > 2:
        score += ord(str(key[2])[0])

    return score


def test_login():
    """
        lsusb | more
    Bus 002 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub

    ok
    Bus 001 Device 003: ID 2c7c:0125 Quectel Wireless Solutions Co., Ltd. EC25 LTE modem


    Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub

        lspci
    00:00.0 Host bridge: Intel Corporation Atom Processor Z36xxx/Z37xxx Series SoC Transaction Register (rev 0e)
    00:02.0 VGA compatible controller: Intel Corporation Atom Processor Z36xxx/Z37xxx Series Graphics & Display (rev 0e)
    00:13.0 SATA controller: Intel Corporation Atom Processor E3800 Series SATA AHCI Controller (rev 0e)
    00:14.0 USB controller: Intel Corporation Atom Processor Z36xxx/Z37xxx, Celeron N2000 Series USB xHCI (rev 0e)
    00:1a.0 Encryption controller: Intel Corporation Atom Processor Z36xxx/Z37xxx Series Trusted Execution Engine (rev 0e)
    00:1b.0 Audio device: Intel Corporation Atom Processor Z36xxx/Z37xxx Series High Definition Audio Controller (rev 0e)
    00:1c.0 PCI bridge: Intel Corporation Atom Processor E3800 Series PCI Express Root Port 1 (rev 0e)
    00:1c.1 PCI bridge: Intel Corporation Atom Processor E3800 Series PCI Express Root Port 2 (rev 0e)
    00:1c.2 PCI bridge: Intel Corporation Atom Processor E3800 Series PCI Express Root Port 3 (rev 0e)
    00:1c.3 PCI bridge: Intel Corporation Atom Processor E3800 Series PCI Express Root Port 4 (rev 0e)
    00:1f.0 ISA bridge: Intel Corporation Atom Processor Z36xxx/Z37xxx Series Power Control Unit (rev 0e)
    00:1f.3 SMBus: Intel Corporation Atom Processor E3800/CE2700 Series SMBus Controller (rev 0e)

    ok
    01:00.0 Ethernet controller: Intel Corporation 82583V Gigabit Network Connection
    02:00.0 Ethernet controller: Intel Corporation 82583V Gigabit Network Connection
    03:00.0 Ethernet controller: Intel Corporation I350 Gigabit Fiber Network Connection (rev 01)
    03:00.1 Ethernet controller: Intel Corporation I350 Gigabit Fiber Network Connection (rev 01)


    """
    text = """
    asda
    """

    pattern = """(?msx)
    \s*
    (?P<_index_>\d+):\s+
    (?P<device>[^:]+):\s+

    (?P<body>.*?
        link/
          (?P<link>loopback|ether|none)\s+
          (?P<mac>[\d:]+)\s+
        brd\s+
        (?P<brd>[\d:]+)\s+
        .*?
        (
          inet\s+
          (?P<ipv4>\d+\.\d+\.\d+\.\d+/\d+)\s
          scope
        )?
    .*?
    )
    (?=\d+:\s+\w+)

    (?P<_tail_>.*)
    """

    # pattern2 = """(?msx)
    # \s*
    # (?P<device>[^:]+):\s+
    ##(?P<body>.*)
    # (?!\d+:\s+\w+)

    # (?P<_tail_>.*?)
    # """
    m = True
    while m:
        m = re.search(pattern, text)
        if m:
            d = m.groupdict()
            text = d.pop("_tail_")
            print(d)
            foo = 1
    foo = 1

    stream = [
        [(), "<dict>"],
        [("a",), 1],
        [("b",), 2],
        [("z",), "<list>"],
        [("z", 0), "foo"],
        [("z", 5), "bar"],
        [("x",), "<dict>"],
        [("x", 1), "99"],
        [("x", 5), "55"],
    ]

    data = rebuild(stream)

    reactor = Reactor()
    # ssh = SShell(hostname='venoen243')
    ssh = SShell(hostname="wvenoen134")

    settler = Settler(name="settler", shell=ssh)
    reactor.attach(settler)

    run(reactor.main())

    yaml.dump(settler.ctx, open("settler.yaml", "wt"), Dumper=yaml.Dumper)

    foo = 1


def test_compression():
    """Just testing sending blueprint iver UDP"""
    # compression tests ----------
    blueprint = open("blueprint.venoen.txt").read().encode("utf-8")

    l0 = len(blueprint)
    lxz = len(xz.compress(blueprint))
    lxzx = len(xz.compress(blueprint, preset=9 | xz.PRESET_EXTREME))

    lbz = len(bz2.compress(blueprint))
    lgz = len(gzip.compress(blueprint))


def test_process_offline_interaction():
    shell = Executor()
    settler = Settler(name="settler", shell=shell)

    blueprint = open("blueprint.venoen.txt").read()
    settler.process_interations(blueprint)
    foo = 1


def test_get_status():
    reactor = Reactor()
    # ssh = SShell(hostname='venoen243')
    # ssh = SShell(hostname='localhost', username='agp')
    ssh = AsyncShell(hostname="localhost", username="agp")

    settler = Settler(name="settler", shell=ssh)
    reactor.attach(settler)

    run(reactor.main())

    yaml.dump(settler.ctx, open("settler.yaml", "wt"), Dumper=yaml.Dumper)
    foo = 1


def test_asyncssh():
    async def run_client() -> None:
        async with asyncssh.connect("localhost") as conn:
            async with conn.create_process(
                "sudo apt install python3-selenium"
            ) as process:
                while True:
                    output = await process.stdout.readline()
                    print(
                        f"---> [{process.exit_status}] [{process.is_closing()}] {output}"
                    )
                    await sleep(0.25)
                    if process.exit_status is not None:
                        break
            foo = 1

            # for op in ['2+2', '1*2*3*4', '2^32']:
            # process.stdin.write(op + '\n')
            # result = await process.stdout.readline()
            # print(op, '=', result, end='')

    try:
        asyncio.get_event_loop().run_until_complete(run_client())
    except (OSError, asyncssh.Error) as exc:
        sys.exit("SSH connection failed: " + str(exc))


def test_gather_facts():
    reactor = Reactor()

    conn = DefaultExecutor()
    reactor.attach(conn)

    stm = CPUInfoFact()
    reactor.attach(stm)

    stm = DiskInfoFact()
    reactor.attach(stm)

    stm = IPInfoFact()
    reactor.attach(stm)

    stm = DiskInfoFact()
    reactor.attach(stm)

    stm = FileContentFact(name="/etc/hosts", prefix="real.etc.hosts")
    reactor.attach(stm)

    stm = DebListFact()
    reactor.attach(stm)

    stm = PipListFact()
    reactor.attach(stm)

    run(reactor.main())
    reactor.save()

    kk = yaml.load(open("reactor.yaml", "rt"), Loader=yaml.Loader)
    foo = 1


def test_apply_state():
    reactor = Reactor()
    conn = DefaultExecutor()
    reactor.attach(conn)

    stm = Pastor()
    reactor.attach(stm)

    run(reactor.main())
    # reactor.save()

    # kk = yaml.load(open('reactor.yaml', 'rt'), Loader=yaml.Loader)
    # foo = 1


if __name__ == "__main__":
    # test_login()
    # test_process_offline_interaction()
    # test_get_status()
    # test_asyncssh()
    # test_gather_facts()
    data = yaml.load(open("example.target.yaml"), Loader=yaml.Loader)

    test_apply_state()
