import sys
import os
import re
import hashlib
import random
import time
import inspect
import shutil
import getpass

sys.path.append(os.path.abspath('.'))

import semver

from pycelium.tools.containers import simplify, merge
from pycelium.tools import expandpath

from .definitions import (
    DEB_FACTS,
    DEB_AVAILABLE_FACTS,
    FS_FACTS,
    SERVICE_STATUS_FACTS,
    SERVICE_STATUS_FACTS,
    TARGET,
    PIP_FACTS,
    SERVICE_FACTS,
    DEINSTALL,
    INSTALL,
    LASTEST,
    LOCALE_PREFERENCES,
    REAL_LOCALE_PREFERENCES,
    NEEDS_INSTALL,
    NEEDS_UNINSTALL,
    REPO_PREFERENCES,
    T_TPL_LOCATION,
    TPL_LOCATION,
)

from .shell import (
    assign,
    bspec,
    tspec,
    update,
    walk,
    glom,
    T,
    Finder,
    jinja2regexp,
    jinja2template,
    temp_filename,
)

from .action import Action
from .agent import Agent
from .packages import DebPkgInstall
from .gathering import GatherFact, DebListFact


class HashFileFact(GatherFact):
    """
    TBD
    """

    def __init__(self, merge=True, prefix=FS_FACTS, *args, **kw):
        super().__init__(merge=merge, prefix=prefix, *args, **kw)
        self.cmdline = "sha1sum {{ name }}"

    def _populate_interactions(self):
        super()._populate_interactions()
        self.add_interaction(
            '200_get_file_hash',
            r'(?P<sha1>[a-z0-9]{40})\s+(?P<key>.*?)(\n|$)',
            'set_object',
        )
        self.add_interaction(
            '400_cli_warning',
            r'\s*WARNING:.*?(\n|$)',
        )


class FileFact(GatherFact):
    """
        ls -li {{ pattern }}
        (?P<inode>\d+)?\s*(?P<perm>[-drwxSt]+)\s*\d+\s*(?P<uid>[^\s]+)\s*(?P<gid>[^\s]+)\s*(?P<size>\d+)\s*(?P<date>\w+\s+\d+\s+[\d:]+)\s+(?P<key>.*)(\n|$)

        stat {{ pattern }}
        stat /etc/grafana/grafa*
      File: /etc/grafana/grafana.conf
      Size: 50        	Blocks: 8          IO Block: 4096   regular file
    Device: fd00h/64768d	Inode: 6029345     Links: 1
    Access: (0664/-rw-rw-r--)  Uid: ( 1000/    user)   Gid: ( 1000/    user)
    Access: 2023-04-21 19:42:28.184611320 +0000
    Modify: 2023-04-21 19:35:21.721303863 +0000
    Change: 2023-04-21 19:35:25.309264166 +0000
     Birth: 2023-04-21 19:35:21.713303953 +0000
      File: /etc/grafana/grafana.ini
      Size: 54215     	Blocks: 112        IO Block: 4096   regular file
    Device: fd00h/64768d	Inode: 4325499     Links: 1
    Access: (0640/-rw-r-----)  Uid: (    0/    root)   Gid: (  121/ grafana)
    Access: 2023-04-21 18:25:58.806756605 +0000
    Modify: 2023-04-20 14:47:15.056299102 +0000
    Change: 2023-04-20 14:47:15.140298048 +0000
     Birth: 2023-04-20 14:47:15.056299102 +0000



      File: backups.service -> /home/agp/.config/systemd/user/backups.service
      Size: 46        	Blocks: 0          IO Block: 4096   symbolic link
    Device: 10302h/66306d	Inode: 11409909    Links: 1
    Access: (0777/lrwxrwxrwx)  Uid: ( 1000/     agp)   Gid: ( 1000/     agp)
    Access: 2023-04-22 08:26:13.476983709 +0200
    Modify: 2022-12-15 00:44:08.782292294 +0100
    Change: 2022-12-15 00:44:08.782292294 +0100
     Birth: 2022-12-15 00:44:08.782292294 +0100



    """

    def __init__(self, merge=True, prefix=FS_FACTS, *args, **kw):
        super().__init__(merge=merge, prefix=prefix, *args, **kw)
        self.cmdline = "stat {{ name }}"

    def _populate_interactions(self):
        super()._populate_interactions()
        self.add_interaction(
            '200_get_file_name',
            r'File:\s+(?P<key>.*?)(\n|$)',
            'new_group',
        )
        self.add_interaction(
            '201_get_size',
            r'Size:\s+(?P<size>\d+)\s+Blocks:\s+(?P<blocks>\d+)\s+IO\sBlock:\s+(?P<ioblocks>\d+)\s+(?P<type>.*)(\n|$)',
            'merge_object',
        )
        self.add_interaction(
            '202_get_inode',
            r'Device:\s+(?P<device>[^\s]+)\s+Inode:\s+(?P<inode>\d+)\s+Links:\s+(?P<links>\d)\s*(\n|$)',
            'merge_object',
        )
        self.add_interaction(
            '203_get_owner',
            r'Access:\s+\((?P<mode>\d+)\/(?P<hmode>.*?)\)\s+Uid:\s*\(\s*(?P<uid>\d+)\/\s*(?P<owner>.*?)\)\s+Gid:\s\(\s*(?P<gid>\d+)\/\s*(?P<group>.*?)\)(\n|$)',
            'merge_object',
        )
        self.add_interaction(
            '204_get_date',
            r'(?P<key>\w+):\s(?P<value>\d+-\d+-\d+\s+\d+:\d+:\d+\.\d+\s+[+-]\d+)(\n|$)',
            'indirect_set_attribute',
        )


class SystemUnitAvailableFact(GatherFact):
    """
    TBD
    """

    def __init__(self, merge=True, prefix=SERVICE_STATUS_FACTS, *args, **kw):
        super().__init__(merge=merge, prefix=prefix, *args, **kw)
        self.cmdline = "ls -l /lib/systemd/system/"

    def _populate_interactions(self):
        super()._populate_interactions()
        #   UNIT LOAD ACTIVE SUB DESCRIPTION

        self.add_interaction(
            '200_get_unit-state',
            r'(?P<key>[^\s]+)\s*(\n|$)',
            'set_object',
        )
        # self.add_interaction(
        #'250_header',
        # r'UNIT\s+LOAD\s+ACTIVE\s+SUB\s+DESCRIPTION\n',
        # )


class SystemUnitInventoryFact(GatherFact):
    """
    TBD
    """

    def __init__(self, merge=True, prefix=SERVICE_STATUS_FACTS, *args, **kw):
        super().__init__(merge=merge, prefix=prefix, *args, **kw)
        self.cmdline = "systemctl list-units"

    def _populate_interactions(self):
        super()._populate_interactions()
        #   UNIT LOAD ACTIVE SUB DESCRIPTION

        self.add_interaction(
            '200_get_unit-state',
            r'(?P<key>[^\s]+)\s+(?P<load>[^\s]+)\s+(?P<active>[^\s]+)\s+(?P<running>[^\s]+)\s+(?P<sub>[^\s]+)\s+(?P<description>[^\s]+)\s*(\n|$)',
            'set_object',
        )
        self.add_interaction(
            '150_header',
            r'UNIT\s+LOAD\s+ACTIVE\s+SUB\s+DESCRIPTION\n',
        )


class SystemUnitFact(GatherFact):
    """
    TBD
    """

    def __init__(self, merge=True, prefix=SERVICE_STATUS_FACTS, *args, **kw):
        super().__init__(merge=merge, prefix=prefix, *args, **kw)
        self.cmdline = "systemctl status {{ unit_name }}"

    def _populate_interactions(self):
        super()._populate_interactions()
        #   UNIT LOAD ACTIVE SUB DESCRIPTION

        self.add_interaction(
            '200_get_unit-state',
            r"""(?imxs)[^\s]+\s(?P<key>[^\s]+)[\s-]+(?P<description>[^\n]+)
            \s+Loaded:\s+(?P<loaded>[^\s]+)\s+\((?P<unit_path>[^\s;]+).*?\)
            \s+
            Active:\s(?P<status>[^\s]+)\s+\((?P<reason>.*?)\)
            \s*
            (since\s+(?P<since>[^\n]+))?
            """,
            'set_object',
            preserve_key=True,
        )


class SystemUnitPathFact(SystemUnitFact):
    def __init__(self, path, restart_path, *args, **kw):
        super().__init__(*args, **kw)
        self.path = path
        self.restart_path = restart_path

    async def _enter_stop(self, *args, **kw):
        # extend 'path' sub-section for parent service
        spec = bspec(self.prefix)
        status = self.g(
            spec,
            self.restart_path,
            'status',
            default='unkown_path',
            _target_=self.facts,
        )
        data = {
            SystemUnitPath.MONITOR_KEYWORD: {
                self.path: status,
            },
        }
        self.s(bspec(self.prefix, self.name), data, _target_=self.facts)
        await super()._enter_stop(*args, **kw)


class SystemUnitAction(Action):
    """
    TBD
    """

    KLASS = SystemUnitFact

    def __init__(
        self,
        user=False,
        force=False,
        enable=True,
        action='',
        *args,
        **kw,
    ):
        super().__init__(*args, **kw)
        self.unit_name = self.name
        self.enable = enable
        self.force = force

        self.user = user
        self.action = action
        self.cmdline = "{{ 'sudo' if not user }} systemctl {{ '--user' if user }} {{ action }} {{ unit_name }}"

    def _populate_interactions(self):
        super()._populate_interactions()
        self.add_interaction(
            '404_unit-failed',
            r'Failed.*enable\s+unit:\s+Unit\s+file\s+(?P<path>.*?(?P<service>[^\s\/]+))\s+is\s+(?P<reason>[^\s\.]+)[\.\s]*',
            'unit_failed',
        )

    async def _enter_boot(self, *args, **kw):
        action = self.new_action(self.KLASS, **self.__dict__)
        result = await self.wait(action)
        if any(result):
            self.force = True

        self.action = ''
        if self.force:
            if self.enable:
                self.action = 'reload-or-restart'
            else:
                self.action = 'disable'
        else:
            info = self.g(action.prefix, self.unit_name, default={})
            if self.enable:
                # SystemUnitAvailableFact: ls -l /lib/systemd/system/
                # SystemUnitInventoryFact: systemctl list-units
                if info.get('status') not in ('active',):
                    self.action = 'enable --now'
            else:
                if info.get('status') not in ('inactive',):
                    self.action = 'stop'

        if not self.action:
            self.log.debug(f"Unit: {self.unit_name} is Ok, nothing to do")
            self._term()
        else:
            await super()._enter_boot(*args, **kw)

    async def _interact_unit_failed(self, match, **kw):
        """
        d
        {'path': '/lib/systemd/system/wg-quick@wg-project.service',
         'service': 'wg-quick@wg-project.service',
         'reason': 'masked'}
        """
        d = match.groupdict(default='')
        d.update(kw)

        commands = {
            'masked': 'systemctl unmask {{ service }}',
        }

        result = False
        command = commands.get(d.get('reason'))
        if command:
            result = await self.execute(command, sudo=True, **d)

        if result:
            self.restart = 1
        return result
        # assign(self.facts, spec, value)


class SystemUnitUnmask(SystemUnitAction):
    """
    TBD
    """

    def __init__(self, enable=True, *args, **kw):
        action = 'unmask' if enable else 'mask'
        super().__init__(action=action, *args, **kw)

    async def _enter_boot(self, *args, **kw):
        m = re.match(REG_IS_TEMPLATE_UNIT, self.name)
        if m:
            self.ctx.update(m.groupdict())
            self.unit_name = self.expand('{{ prefix }}@.service', **kw)
        await super()._enter_boot(*args, **kw)


class SystemUnitEnable(SystemUnitAction):
    """
    TBD
    """

    def __init__(self, enable=True, *args, **kw):
        action = 'enable' if enable else 'disable'
        super().__init__(action=action, *args, **kw)


class SystemUnitStart(SystemUnitAction):
    """
    TBD
    """

    def __init__(self, force=False, enable=True, *args, **kw):
        super().__init__(*args, **kw)
        self.enable = enable
        self.force = force


REG_IS_TEMPLATE_UNIT = r'(?P<prefix>[^\@]+)@(?P<subname>.*)\.service'


class SystemUnitPath(SystemUnitAction):
    """
    self.name: 'wg-quick@wg-xxx.service'
    self.path: '/etc/wireguard/wg-xxx.conf'

    restart_unit: restart-wg-quick@wg-xxx.service
    restart_path: restart-wg-quick@wg-xxx.path

    """

    KLASS = SystemUnitPathFact
    MONITOR_KEYWORD = 'watch'

    def __init__(self, path, *args, **kw):
        super().__init__(*args, **kw)
        self.path = path

        self.restart_service = ''
        self.restart_path = ''

    async def _enter_boot(self, *args, **kw):
        base, ext = os.path.splitext(self.name)
        assert ext in ('.service',)
        assert self.path
        tpath = expandpath(self.path).replace('/', '.')[1:]

        self.restart_service = self.expand(
            'restart-{{ base }}.service', **kw
        )
        self.restart_path = self.expand(
            'restart-{{ base }}-{{ tpath }}.path', **kw
        )
        self.unit_name = self.restart_path

        await super()._enter_boot(*args, **kw)

    async def _enter_stop(self, *args, **kw):
        await super()._enter_stop(*args, **kw)

    async def _enter_kill(self, *args, **kw):
        await super()._enter_kill(*args, **kw)

    async def _write_unit(self, content, name, **kw):
        path = self.expand('/lib/systemd/system/{{ name }}', name=name, **kw)
        kw.setdefault('owner', 'root')
        kw.setdefault('group', 'root')
        kw.setdefault('mode', '644')
        await self.create_file(path, content=content, **kw)

        return True

    async def _seq_10_path_restart(self, *args, **kw):
        template = """
# Description=Restart {{ name }} service
[Service]
Type=OneShot
ExecStart=/usr/bin/systemctl restart {{ name }}

[Install]
WantedBy=multi-user.target
# end

"""
        content = self.expand(template, **kw)
        result = await self._write_unit(content, self.restart_service)
        return result

    async def _seq_20_path_path(self, *args, **kw):
        template = """
# Description=Restart {{ name }} when {{ path }} changes
[Path]
Unit={{ restart_service }}
PathChanged={{ path }}

[Install]
WantedBy=multi-user.target
# end

"""

        content = self.expand(template)
        result = await self._write_unit(content, self.restart_path)
        return result

    async def _seq_30_path_enable(self, *args, **kw):
        if self.enable:
            action = self.new_action(
                SystemUnitStart, name=self.restart_path, enable=True
            )
            result = await self.wait(action)
            return not any(result)
        return True


class SystemdUnitState(Agent):
    """
    TBD
    """

    def __init__(self, enable=True, *args, **kw):
        super().__init__(*args, **kw)
        self.enable = enable

    def _populate_interactions(self):
        super()._populate_interactions()
        # self.add_interaction(
        #'404_give_me_passwd',
        # r'.*Pass.*',
        # )

    async def _hide_seq_10_unit_unmask(self, *args, **kw):
        action = self.new_action(SystemUnitUnmask, **self.__dict__)
        result = await self.wait(action)
        return not any(result)

    async def _hide_seq_20_unit_enable(self, *args, **kw):
        action = self.new_action(SystemUnitEnable, **self.__dict__)
        result = await self.wait(action)
        return not any(result)

    async def _seq_30_unit_restart(self, *args, **kw):
        action = self.new_action(SystemUnitStart, **self.__dict__)
        result = await self.wait(action)
        return not any(result)

    async def _hide_seq_40_unit_path(self, *args, **kw):
        if self.path:
            action = self.new_action(SystemUnitPath, **self.__dict__)
            result = await self.wait(action)
            return not any(result)
        return True


class SystemdDaemonReload(Action):
    """
    TBD
    """

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.cmdline = "systemctl daemon-reload {{ lang }}"

    def _populate_interactions(self):
        super()._populate_interactions()
        self.add_interaction(
            '404_give_me_passwd',
            r'.*Pass.*',
        )


class LocateGen(GatherFact):
    """
    TBD
    """

    def __init__(
        self, merge=True, prefix=REAL_LOCALE_PREFERENCES, *args, **kw
    ):
        super().__init__(merge=merge, prefix=prefix, *args, **kw)
        self.cmdline = "locale-gen {{ lang }}"

    def _populate_interactions(self):
        super()._populate_interactions()

        self.add_interaction(
            '200_get_unit_state',
            r'\s*(?P<key>.*?)\.+\s+(?P<value>done)(\n|$)',
            #'set_object',
            'set_attribute',
        )
        self.add_interaction(
            '100_header',
            r'Generating\s+locales.*?(\n|$)',
        )

        self.add_interaction(
            '299_generation_complete',
            r'.*Generation\s+complete.*',
        )


class DebAptUpdate(Action):
    """
    TBD
    """

    def __init__(self, warm_body=600, *args, **kw):
        super().__init__(warm_body=warm_body, *args, **kw)
        self.cmdline = "apt update"

    def _populate_interactions(self):
        super()._populate_interactions()
        self.add_interaction(
            '200_get_repo_url',
            r'(?P<action>Hit|Get|Ign):(?P<seq>\d+)\s+(?P<url>[^\s]+).*?(\n|$)',
            #'set_object',
        )

        self.add_interaction(
            '200_building_tree',
            r'\sBuilding\s+dependency\s+tree.*?(\n|$)',
        )
        self.add_interaction(
            '400_cli_warning',
            r'\s*(WARNING|W):.*?(\n|$)',
        )


class ChangeLocale(Action):
    """
    TBD
    """

    def __init__(self, lang='en_US.UTF-8', *args, **kw):
        self._stop_no_seq = False  # wait until fibers have done
        self.lang = lang
        super().__init__(*args, **kw)
        foo = 1

    # --------------------------------------------------
    # Coded as sequence: # TODO: review
    # --------------------------------------------------
    async def _seq_10_locale_add(self, *args, **kw):
        try:
            action = self.new_action(
                Action,
                cmdline="update-locale LANG={{ lang }} LC_MESSAGES=POSIX",
            )
            action.ctx['lang'] = self.lang
            await self.wait(action)
            return True
        except Exception as why:
            self.log.exception(why)
        return False

    async def _seq_20_locale_gen(self, *args, **kw):
        try:
            # self.push(self.EV_TERM)
            action = self.new_action(LocateGen)
            action.ctx['lang'] = self.lang
            await self.wait(action)
            return True
        except Exception as why:
            self.log.exception(why)
        return False

    async def _seq_99_locale_test(self, *args, **kw):
        try:
            # self.push(self.EV_TERM)
            # action = self.new_action(LocateGen)
            # await self.wait(action)
            if (
                glom(
                    self.reactor.ctx, REAL_LOCALE_PREFERENCES, default={}
                ).get(self.lang.lower())
                == 'done'
            ):
                self.log.info(f"Locale for LANG='{self.lang}' OK")
            else:
                self.log.disabled(f"Locale for LANG='{self.lang}' FAILED")

            return True
        except Exception as why:
            self.log.exception(why)
        return False


class AddSudoers(Action):
    """
    TBD
    """

    def __init__(self, *args, **kw):
        self._stop_no_seq = False  # wait until fibers have done
        super().__init__(*args, **kw)
        foo = 1

    # --------------------------------------------------
    # Coded as sequence: # TODO: review
    # --------------------------------------------------
    async def _seq_10_sudoers_add(self, *args, **kw):
        try:
            executor = await self.is_connected()
            user = executor.user

            owner = group = 'root'
            path = '/etc/sudoers.d/{{ user }}_no_passwd'
            content = '{{ user }} ALL=(ALL:ALL) NOPASSWD:ALL'

            await self.create_file(
                path, content, owner=owner, group=group, mode='600'
            )
            # self.push(self.EV_KILL)
            return True
        except Exception as why:
            self.log.exception(why)
        return False

    async def _seq_99_sudoers_test(self, *args, **kw):
        try:
            # self.push(self.EV_TERM)
            action = self.new_action(SystemdDaemonReload)
            await self.wait(action)

            executor = await self.is_connected()
            user = executor.user
            if action.history or action.process.exit_status > 0:
                self.log.error(
                    f"Add '{user}' to sudoers failed, still require password!"
                )
            else:
                self.log.info(f"Add '{user}' to sudoers OK")
            return True
        except Exception as why:
            self.log.exception(why)
        return False

    # --------------------------------------------------
    # Interactions
    # --------------------------------------------------
    def _populate_interactions(self):
        super()._populate_interactions()
        # self.add_interaction(
        #'200_get_repo_url',
        # r'(?P<action>Hit|Get|Ign):(?P<seq>\d+)\s+(?P<url>[^\s]+).*?(\n|$)',
        ##'set_object',
        # )

        # self.add_interaction(
        #'200_building_tree',
        # r'\sBuilding\s+dependency\s+tree.*?(\n|$)',
        # )
        # self.add_interaction(
        #'400_cli_warning',
        # r'\s*(WARNING|W):.*?(\n|$)',
        # )


def closer_match(candidates, token, min_score=0.95):
    b_score, b_candidate, b_len = -1, None, 0
    for candidate in candidates:
        if token in candidate:
            l0 = len(token)
            l1 = len(candidate)
            score = 2 * l0 / (l0 + l1)
            if score >= min_score and (
                score > b_score or (score == b_score and l0 > b_len)
            ):
                b_score, b_candidate, b_len = score, candidate, l0
    return b_candidate, b_score


def guess_action(available, installed, desired, min_score=0.8, console=None):
    for name, version in desired.items():
        if version in NEEDS_UNINSTALL:
            candidate, score = closer_match(installed, name, min_score)
            if candidate:  # else, ingnore, not enough score
                yield candidate, DEINSTALL
            else:
                console and console(
                    f"Ignoring '{name}' for '{version}', no similar package installed!!"
                )

        else:
            # check specific version to install
            i_candidate, i_score = closer_match(installed, name, min_score)
            a_candidate, a_score = closer_match(available, name, min_score)

            if a_candidate:
                if a_score >= 1.00:
                    console and console(
                        f"Found an exact match for: '{name}', nice!"
                    )
                else:
                    console and console(
                        f"Found an partial match for: '{name}' -->'{a_candidate}' score={a_score}"
                    )

                # exist an availale version
                if not i_candidate:
                    yield a_candidate, INSTALL
                elif version in (INSTALL):
                    continue  #  NOP
                else:
                    # vesion in (LASTEST, varesion-value

                    # {'distro': 'stable,now', 'version': '9.4.7', 'platform': 'amd64 [installed]'}
                    a_info = available[a_candidate]

                    if version in (LASTEST,):
                        if a_candidate > i_candidate:
                            yield a_candidate, INSTALL
                    else:
                        if version < i_candidate:
                            yield a_candidate, DEINSTALL
                            yield a_candidate, version

                    foo = 1

            else:
                console and console(
                    f"Ignoring '{name}' for '{version}', no similar package found!!"
                )
                pass


def get_semver(version):
    best = version
    parse = semver.Version.parse
    for i in range(1, len(version)):
        text = version[:i]
        try:
            best = parse(text)
        except ValueError:
            continue
    return best


def guess_action2(
    available1, available0, desired, min_score=0.8, console=None
):
    for name, version in desired.items():
        candidate, score = closer_match(available1, name, min_score)

        if version in NEEDS_UNINSTALL:
            if candidate:  # else, ingnore, not enough score
                yield candidate, DEINSTALL
            else:
                console and console(
                    f"Ignoring '{name}' for '{version}', no similar package installed!!"
                )
        else:
            # check specific version to install
            if candidate:
                info1 = available1.get(candidate, {})
                info0 = available0.get(candidate, {})

                if score >= 1.00:
                    console and console(
                        f"Found an exact match for: '{name}', nice!"
                    )
                else:
                    console and console(
                        f"Found an partial match for: '{name}' -->'{candidate}' score={score}"
                    )

                # exist an availale version
                if info1['status'] in (
                    '',
                    None,
                ):
                    yield candidate, INSTALL
                elif version in (INSTALL):
                    continue  #  NOP, is just satisfied
                else:
                    # vesion in (LASTEST, varesion-value)
                    # info
                    # {'distro': 'jammy-updates,jammy-security,now',
                    #'version': '1.6.7~rc0-1ubuntu0.22.04.1',
                    #'platform': 'amd64',
                    #'status': 'installed',
                    #'update': ''}
                    ver0 = get_semver(info0.get('version', version))
                    ver1 = get_semver(info1.get('version', version))

                    if version in (LASTEST,):
                        if ver1 > ver0:
                            console and console(
                                f"Upgrading package: '{candidate}' from {ver0} --> {ver1} due '{version}' policy"
                            )
                            yield candidate, INSTALL
                        else:
                            console and console(
                                f"Package: '{candidate}' is in the lastest version: {ver1}, '{version}' policy"
                            )
                    elif version in (INSTALL,):
                        console and console(
                            f"Ignoring upgrade for package: '{candidate}' {ver0} = {ver1} due '{version}' policy"
                        )
                    else:
                        # version is set to an expecific version:
                        ver = get_semver(version)
                        if ver == version:
                            console and console(
                                f"We cant not parse desired version {version} for package: '{candidate}'"
                            )
                        if ver < ver0:
                            console and console(
                                f"DOWNGRADE for package: '{candidate}' from {ver0} --> {ver}"
                            )
                            yield candidate, DEINSTALL
                            yield candidate, version

                    foo = 1

            else:
                console and console(
                    f"Ignoring '{name}' for '{version}', no similar package found!!"
                )
                pass


class Service(Agent):
    """
    myviewer:
        users:
            melange:
                sudo: true
                password: Three Litle Cats
                uid: 9000
                guid: 9000
                keys:
                    - ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQCmqk2kaN+z1SPJZLKFng31RGF3JlGD4mle6MAitDL3J5Tmp8OaaqQHtbhZskIlLjurZsbE0kzV2+fpNsHzR9FSdJF+KZU3EbLIxN161lM6Gv8KtV0uuU7bg+D2czwtpazo4xVz0xdHQJ+zsXSL77y5sEKkifWbLim2G4ZWM7jkOUFGVDOMrbWEjsNKXQysCR2EFBtI+sFqS+08/ipqUf4j2jINjSEu+JHknQ1izysAoT6BuZ9lwarGjkuOrNJZ40qUZUOOUcnbRzMeLJFyl3sRBW6dSxkDCkG/xewLfgB9qBMBAdd+Lw64SN7W2eWKd3HQWAv+ms+Uqv6x/wksyYWz+K1q+LJtD3QbdLNXHWo66G+xXKiIAyjged4k/2YVQMMxnLHB9cEKpq13vCoTHo0amifgkYyQQqKH1YK1ek7Qknf1N5i6k85ICsYy9eAea2bA62uB3hJaVDuq1Pnfg6SE/H8c0WfZqHl65M+5ra0iW8pcZD4+u3xHVc03phji00E= agp@dev00
                    - ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQC4K12CJkL6cjqC2T/S9rVbP0oLd6FGAHuiKUJqu3WCPHSDL98G6sR5t4MW/IH6SmnIoSB2tLGyPDQo4ies6JWesktn7FWIDk6Nb0l3IrQShEbc/gPyFXL5mWpmWZ5NrAJutO17Y+/p1eyrFw1i1QtdBljboaYGA8EIuUCy+YLHAHP44SXts5nXizFEXiM/GJTeenPc0Jfhe5YlkZvFQBGCRMIpM6FyliEaEQZNtNo5jXlEFcaqBwQJVuvwRa92P9mp7HhbXP8Qq5NN/bhSmCgQoYOn5UKHoV/xpNy/i4jhPZRsKMEpX6XcO+CTWmkUlhuAQFOW1csOTlCag01pwbvhK3MiXGpmZutZrY9SX4aOpL4Hf3VtxYWGeb4Awczz/zI4QHqD4iiOAgYksjR9BiahDo1lFPcFi2hlvbwDPZCJRq5hGddruJw93tEtpecIMmYV8aZSV+ifgdsGXG6IYoUAR1UpJKDuhPut+Y4/QgBEB5BaEgvogx7CcuHXaHCRSUc= agp@dietpi
            melange:
                sudo: true
                password: Three Litle Cats Jumping
                uid: 9001
                guid: 9001
        repositories:
            grafana:
                key: https://packages.grafana.com/gpg.key
                url: deb [trusted=yes] https://packages.grafana.com/oss/deb stable main
            influx:
                key: https://repos.influxdata.com/influxdb.key
                url: deb [trusted=yes] https://repos.influxdata.com/debian stable main
        packages:
            influxdb: lastest  # '==10.2.1'
            telegraf: lastest  # '>=12.1'
            grafana: lastest
            foo: uninstall
        templates:
            "{{ service }}/{{ item }}.conf.j2":
                dest: /etc/{{ service }}/{{ item }}.conf
                owner: root
                mode: 0o600
            # this can be also done:
            #   tpl/grafana/grafana.conf.j2  ---> /etc/grafana/grafana.conf
            #   tpl/influx/influx.conf.j2    ---> /etc/influx/influx.conf
            "(?P<fullpath>.*?).j2":
                dest: /etc/{{ fullpath }}.conf
                owner: root
                mode: 0o600
            "bin/(?P<name>.*?).sh":
                dest: /usr/local/bin/{{ name }}.sh
                owner: root
                mode: a+rx

        services:
            influxdb: system   # user
            telegraf: system
            grafana-server: system




    """

    def __init__(self, service_name=None, restart=10, *args, **kw):
        super().__init__(restart=restart, *args, **kw)
        # self.FACT_PREFIX = {}
        self.MANIFEST = {}
        # self.TEMPLATES = {}

        preferences = {
            REPO_PREFERENCES: ['deb', 'pip', 'snap'],
            T_TPL_LOCATION: [
                './templates',
                '/etc/templates',
                '/usr/share/templates',
            ],
        }
        for spec, value in preferences.items():
            assign(self.MANIFEST, bspec(spec), value, missing=dict)

        self.service_name = service_name or self.__class__.__name__.lower()
        self.templates = {}
        self.services = {}
        foo = 1

    def _reload_manifest(self):
        path = self.expand('{{ service_name}}.yaml')
        if os.access(path, os.F_OK):
            manifest = self.load(path)
            self.log.info(f"Ok: manifest: '{path}' loaded")
            return manifest
        self.log.error(f"can't load manifest: '{path}'")
        foo = 1

    # ----
    #
    # ----
    async def _boot_manifest_defaults(self, *args, **kw):
        spec = tspec(TARGET, SERVICE_FACTS, self.service_name, 'packages')
        value = dict(self.PACKAGES)
        self.s(spec, value)
        foo = 1

    def _add_package_dependence(self, *names, source='deb', status=LASTEST):
        root = {
            token.split('.')[-1]: token
            for token in [
                DEB_FACTS,
                PIP_FACTS,
            ]  # TODO: load dynamically and unify with PIP_PREFIX
        }
        root = root[source]
        for name in names:
            spec = bspec(root.split('.'), name)
            assign(self.MANIFEST, spec, status, missing=dict)
            foo = 1

    def _find_files(self, top, template, **kw):
        render = self.reactor.env.from_string
        ctx = self.build_ctx(**kw)
        pattern = jinja2template(render, template, **ctx)
        top = top.lstrip('/')

        for root, folders, files in os.walk(top):
            for name in files:
                path = os.path.join(root, name)
                relpath = path.split(top)[1][1:]
                m = re.search(pattern, relpath)
                if m:
                    yield relpath, m.groupdict()

    async def _write_template(self, name, ctx):
        executor = await self.is_connected()
        if not executor:
            self.log.debug(f"no default_executor found !! (skipping)")
            return

        try:
            # create content
            template = self.reactor.env.get_template(name)
            output = template.render(**ctx)

            # get temporal path
            temp = temp_filename()
            temp = '/tmp/kk'

            # get destination path
            #'/etc/wireguard/{{ item }}.conf'
            dest = self.reactor.env.from_string(ctx.get('dest', name))
            dest = dest.render(**ctx)

            # ctx['temp'] = temp
            # ctx['dest'] = dest

            # check if 'dest' file differs from template rendering
            # blueprint1 = ''
            # check if content has changed

            action = self.new_action(HashFileFact, name=dest)
            await self.wait(action)
            action = self.new_action(FileFact, name=dest)
            await self.wait(action)

            blueprint = {f'.*{dest}': '.*'}
            result = self.reactor.search(blueprint, flat=False)
            result = simplify(result)
            blueprint1 = result.get('sha1')

            async def hide_remove():
                result = await self.execute(
                    'cp "{{ dest }}" "{{ temp }}"',
                    'chown {{ local_uid }} "{{ temp }}"',
                    'chgrp {{ local_gid }} "{{ temp }}"',
                    **ctx,
                )
                if result:
                    # check if connectino is remote or local
                    executor = await self.is_connected()
                    if executor.isremote:
                        await executor.get(temp, temp)

                    blueprint1 = hashlib.sha1(
                        open(temp, 'r+b').read()
                    ).hexdigest()

                else:
                    self.log.warning(
                        f"Failed to compute destination blueprint: {dest} (do you have access to files ?)"
                    )

            blueprint0 = hashlib.sha1(
                bytes(output.encode('utf-8'))
            ).hexdigest()

            result = blueprint0 != blueprint1  # same hash?
            if result:
                self.log.debug(f"file content differs: updating {dest}")
                open(temp, 'w').write(output)
                executor = await self.is_connected()
                if executor.isremote:
                    await executor.put(temp, temp)

                # try to move file to final location
                result = await self.execute(
                    'mkdir -p $(dirname "{{ dest }}")',
                    'mv --force "{{ temp }}" "{{ dest }}"',
                    'chown {{ owner }}:{{ group }} "{{ dest }}"',
                    'chmod {{ mode }} "{{ dest }}"',
                    **ctx,
                )
                if executor.isremote:
                    os.unlink(temp)
                foo = 1
            else:
                self.log.debug(
                    f"file content are the same: '{dest}' will not be modifed"
                )
                # os.unlink(temp)
                foo = 1
            foo = 1
        except Exception as why:
            self.log.exception(why)
            return why
        return result

    async def _check_same_content(self, path, content):
        # TODO: can be done withouy aiofiles ??
        # FIX hashing!!
        try:
            action = self.new_action(HashFileFact, name=path)
            r = await self.wait(action, sleep=0.10)
            if not any(r):
                h1 = self.g(action.prefix, path, 'sha1')

                h2 = hashlib.sha1()
                if isinstance(content, str):
                    content = content.encode('utf-8')
                h2.update(content)
                h2 = h2.hexdigest()

                return h1 == h2

        except Exception as why:
            self.log.exception(why)
        return False

    async def _install_package(self, name, source=None, state=LASTEST):
        """
        - [ ] get repo order preferences: deb, pip, ...
        - [ ] check if package exist in any repo type
        - [ ] check if package is already installed
        """
        if not source:
            m = re.match(r'(deb|pip|snap):(.*)', name)
            if m:
                source, name = m.groups()
            else:
                self.log.error(
                    f"can not determine source from: name={name}, souce={source}"
                )
                return False

        self.log.info(
            f"Trying to install: '{name}' package using: '{source}' source..."
        )

        s = self.subset
        target = self.MANIFEST

        real = glom(
            self.reactor.ctx,
            bspec('real', self.PKG_FACTS, source, default=None),
        )

        if real is None:
            self.log.info(
                f"Can not find current package info for '{source}' source. Try later ..."
            )
            return False

        # localte factory for this source type
        criteria = {
            'mro()': '.*PkgInstall.*',
            'HANDLES': f'.*{source}.*',
        }
        for factory in Finder.find_objects(**criteria):
            break  # just 1st one
        else:
            self.log.error(
                f"no factory found that match {criteria} criteria !!"
            )
            return False

        current = real.get(name)
        a = state in NEEDS_INSTALL
        b = current in NEEDS_INSTALL
        if a ^ b:
            self.new_action(factory, name=name, install=state)
            await self.sleep(5)
        return True

    # --------------------------------------------------
    # Install Sequence
    # --------------------------------------------------
    async def _seq_10_install_users(self, *args, **kw):
        # base = {
        #'foo': {
        #'bar': 'zzzzzzzzzz',
        #'hello': 'world',
        # },
        # }
        # new = {
        #'foo': {
        #'bar': 'xxxxxxx',
        # },
        # }

        # kk = merge(base, new)

        return True

    async def _seq_20_install_repositories(self, *args, **kw):
        """
        - [ ] include keys
        - [ ] add repositories to etc/apt using render template
        - [ ] update repositories


        echo "deb https://cloud.r-project.org/bin/linux/ubuntu  focal-cran40/" | sudo tee /etc/apt/sources.list.d/r-packages.list
        wget -qO- https://cloud.r-project.org/bin/linux/ubuntu/marutter_pubkey.asc | sudo tee -a /etc/apt/trusted.gpg.d/cran_ubuntu_key.asc

        """
        while self.running:
            # await self.sleep()
            self.log.warning("hello _seq_01_install_repositories !!")

            spec = tspec(
                TARGET, SERVICE_FACTS, self.service_name, 'repositories'
            )
            # data = glom(self.reactor.ctx, spec, default=None)
            data = self.g(spec)
            if data is None:
                self.log.debug(
                    f"{self.service_name} does not provide repository info"
                )
                return True

            # if random.random() < 0.15:
            # return True

            for name, info in data.items():
                self.log.debug(f"Checking repository info: {name}: {info}")
                deb_url = info.get('url')
                key_url = info.get('key')
                if all([deb_url, key_url]):
                    # prepare some data
                    deb_url = self.expand(deb_url, **info)
                    key_url = self.expand(key_url, **info)
                    ext = os.path.splitext(key_url)[-1]
                    if '.' not in ext:
                        ext = ''

                    file_list = self.expand(
                        "/etc/apt/sources.list.d/{{ service_name }}.list"
                    )
                    file_key = self.expand(
                        "/etc/apt/trusted.gpg.d/{{ service_name }}{{ ext }}",
                        ext=ext,
                    )
                    # check if repository has been already added
                    if await self._check_same_content(file_list, deb_url):
                        self.log.debug(
                            f"'{file_list}' has same content. Skipping ..."
                        )
                        return True

                    if True:  # TODO: check for sudo presence
                        sudo = 'sudo -S'

                    r1 = await self.execute(
                        'echo -n "{{ deb_url }}" | {{ sudo }} tee {{ file_list }}'
                    )
                    r2 = await self.execute(
                        'wget -qO- {{ key_url}} | {{ sudo }} tee {{ file_key }}'
                    )
                    return r1 and r2
                else:
                    self.log.warning(
                        f"repository info: {info} is not completed, check 'url' and 'key'"
                    )

                foo = 1

    async def _seq_30_install_pkg(self, *args, **kw):
        """
        Translate the Servive.REQUISITES values to Reactor.GOAL.

        and Pastor fibers will handle them

        """
        spec = tspec(TARGET, SERVICE_FACTS, self.service_name, 'packages')
        # desired = glom(self.reactor.ctx, spec, default=None)
        desired = self.g(spec)
        if desired is None:
            self.log.debug(
                f"{self.service_name} does not provide packages to install"
            )
            return True

        names = '|'.join(desired)

        self.log.warning(f"1. Checking packages related with '{names}'")
        t_available0 = self.new_action(DebAvailableFact, pattern=names)
        await self.wait(t_available0)

        self.log.warning(f"2. Updating APT repositories")
        await self.wait(self.new_action(DebAptUpdate, _warm_body=0))

        self.log.warning(
            f"3. Checking newer packages related with '{names}'"
        )

        t_available1 = self.new_action(DebAvailableFact, pattern=names)
        await self.wait(t_available1)

        self.log.warning(
            f"4. Checking installed packages related with '{names}'"
        )
        t_installed = self.new_action(DebListFact, pattern=names)
        await self.wait(t_installed)

        # find best match for package names
        # note: search in filtered results, not in the whole DB system
        available1 = glom(
            t_available1.facts,
            t_available1.prefix,
            default={},
        )
        available0 = glom(
            t_available0.facts,
            t_available0.prefix,
            default={},
        )
        # installed = glom(t_installed.facts, t_installed.prefix, default={})

        actions = {}
        for candidate, action in guess_action2(
            available1, available0, desired, console=self.log.debug
        ):
            self.log.debug(
                f"Guess action for candidate: '{candidate}': ---> {action}"
            )
            actions.setdefault(action, list()).append(candidate)
            foo = 1

        # 1st delete selected packages
        # TODO: use a nested loop and simplify
        names = []
        for action in NEEDS_UNINSTALL:
            names.extend(actions.get(action, {}))

        if names:
            names = '|'.join(names)
            await self.wait(
                self.new_action(DebPkgInstall, name=names, install=False)
            )
            foo = 1

        # 2nd install updated/install packages
        names = []
        for action in NEEDS_INSTALL:
            names.extend(actions.get(action, {}))
            if names:
                names = ' '.join(names)
                await self.wait(
                    self.new_action(
                        DebPkgInstall, name=names, install=INSTALL
                    )
                )
                foo = 1

        return True

    async def _seq_40_install_templates(self, *args, **kw):
        spec = tspec(TARGET, SERVICE_FACTS, self.service_name, 'templates')
        # desired = glom(self.reactor.ctx, spec, default=None)
        desired = self.g(spec)
        if desired is None:
            self.log.debug(
                f"{self.service_name} does not provide packages to install"
            )
            return True

        self.templates.clear()
        for template, info in desired.items():
            # item = self.expand(item)

            # for top in glom(self.reactor.ctx, TPL_LOCATION, default=['.']):
            for top in self.g(TPL_LOCATION, default=['.']):
                found = 0
                for path, d in self._find_files(top, template=template):
                    found += 1
                    ctx = self.build_ctx(info, path=path, **d)
                    r = await self._write_template(path, ctx)
                    self.templates[path] = r, ctx
                    if r in (True,):
                        self.log.debug(
                            f"Ok, dest file '{path}' has been updated: ctx: {ctx}"
                        )
                    elif r in (False,):
                        self.log.debug(
                            f"Ok, dest file '{path}' match. Do not update: ctx: {ctx}"
                        )
                    else:
                        self.log.error(
                            f"Error '{r}' rendering template: {path}: ctx: {ctx}"
                        )

                if found > 0:
                    self.log.info(
                        f"found {found} templates for: '{top}/{template}'"
                    )
                else:
                    self.log.warning(
                        f"Warning: found {found} templates for: '{top}/{template}'"
                    )
                foo = 1
            # service = (
            # f'wg-quick@{item}.service'  # TODO: valid for timers as well
            # )
            # self.SERVICES[service] = ctx.get('user_service')
            foo = 1

        foo = 1

        return True

    async def _seq_50_install_services(self, *args, **kw):
        """
        Restart services based on:
        - [ ] direct settings in 'services' manifest
        - [ ] regular expressions that match some templates
        """
        executor = await self.is_connected()
        if not executor:
            self.log.debug(f"no default_executor found !! (skipping)")
            return

        spec = tspec(TARGET, SERVICE_FACTS, self.service_name, 'services')
        # desired = glom(self.reactor.ctx, spec, default=None)
        desired = self.g(spec)
        if desired is None:
            self.log.debug(
                f"{self.service_name} does not provide services to restart"
            )
            return True

        def get_services():
            used = dict()
            for template, user in desired.items():
                # try to get the service from rendered templates
                for relpath, (modified, info) in self.templates.items():
                    service = self.expand(template, **info)
                    if service:
                        if service not in used:
                            value = user, modified, info
                            used[service] = value
                            yield service, value

        self.services.clear()
        for service, (user, modified, info) in get_services():
            self.log.info(f"Searching Units for service: '{service}'")

            query2 = self.new_action(SystemUnitInventoryFact, pattern='gr')
            await self.wait(query2)

            query1 = self.new_action(
                SystemUnitAvailableFact, pattern=service
            )
            await self.wait(query1)

            units = glom(query1.facts, query1.prefix, default={})
            candidates = (
                service,
                f'{service}-server',
                f'{service}.service',
                f'{service}-server.service',
            )
            for name in candidates:
                self.log.debug(f"trying unit name: '{name}'")
                if name in units:
                    # unit found, restaring
                    if user in (True, 'user'):
                        commands = [
                            'systemctl --user unmask {{ name }}',
                            'systemctl --user enable {{ name }}',
                            'systemctl --user restart {{ name }}',
                        ]
                    else:
                        commands = [
                            'sudo systemctl unmask {{ name }}',
                            'sudo systemctl enable {{ name }}',
                            'sudo systemctl restart {{ name }}',
                        ]

                    self.log.info(
                        f"Found unit name: '{name}': user: '{user}'"
                    )
                    if name in self.services:
                        self.log.warning(
                            f"service '{name}' has been condidered, Skiping..."
                        )
                        break

                    if (
                        modified
                        # or not glom(self.reactor.ctx, query1.prefix)[name]
                        or not self.g(query1.prefix, name)
                    ):
                        result = await executor.exec_many(
                            *commands, name=name
                        )
                        self.services[name] = result
                    else:
                        self.log.info(
                            f"Config files for: '{service}' service wasn't modified, Skipping restarting"
                        )
                        self.services[name] = False
                    break
            else:
                self.log.error(
                    f"Service {service} no found using: {candidates}"
                )

        return True

    # --------------------------------------------------
    # Common transition callbacks
    # --------------------------------------------------
    # ready
    async def _enter_ready(self, *args, **kw):
        self.log.debug(f"{self.__class__.__name__}: do_boot: '{self.name}'")
        manifest = self._reload_manifest()
        if manifest is not None:
            spec = tspec()
            manifest = update(self.MANIFEST, spec, manifest)
            spec = TARGET
            self.m(spec, manifest)

            # update service vars section into self.ctx
            blueprint = {f'.*\\.{self.service_name}\\.vars\.*': '.*'}
            result = self.reactor.search(blueprint, flat=False)
            result = simplify(result)
            merge(self.ctx, result, inplace=True)

            await super()._enter_ready(*args, **kw)
            # self.push(self.EV_WAIT)
        else:
            pass  #  let STM boot without manifest yaml config

        foo = 1

    # running
    async def do_Idle_running_running(self, *args, **kw):
        await super().do_Idle_running_running(*args, **kw)
        self.ctx['sleep'] = 10
