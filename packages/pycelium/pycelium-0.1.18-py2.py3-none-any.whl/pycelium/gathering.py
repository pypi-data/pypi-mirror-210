import sys
import os
from datetime import datetime
from pycelium.tools.containers import deindent_by, search

from .definitions import (
    CPUINFO,
    DEV_INFO,
    DISK_INFO,
    IP_INFO,
    PIP_FACTS,
    DEB_FACTS,
    DEB_AVAILABLE_FACTS,
    DNS_FACTS,
    DEB_REPO_FACTS,
)
from .shell import (
    glom,
    assign,
    bspec,
    tspec,
    norm_key,
    norm_val,
    merge,
    amerge,
)
from .action import Action


class GatherFact(Action):
    def __init__(self, prefix='', merge=True, *args, **kw):
        super().__init__(*args, **kw)
        self.facts = {}
        self.prefix = prefix
        self.merge = merge

        # None will fail, force to set a right value or use _interact_new_group
        self.current_key = []

    async def _enter_running(self, *args, **kw):
        # self.facts = self.reactor.ctx
        # self.merge = None
        await super()._enter_running(*args, **kw)

    async def _interact_new_group(self, match, **kw):
        # d = match.groupdict()
        # d.update(kw)
        self.current_key = [norm_key(t) for t in match.groups() if t.strip()]
        # self.current_key = norm_key('.'.join(match.groups()))

        spec = bspec(self.prefix, self.current_key)
        assign(self.facts, spec, {}, missing=dict)
        foo = 1

    async def _interact_new_nested_group(self, match, prefix='', **kw):
        # d = match.groupdict()
        # d.update(kw)
        self.current_key += [prefix] + [
            norm_key(t) for t in match.groups() if t.strip()
        ]
        # self.current_key = norm_key('.'.join(match.groups()))

        spec = bspec(self.prefix, self.current_key)
        assign(self.facts, spec, {}, missing=dict)
        foo = 1

    async def _interact_set_attribute(
        self, match, preserve_key=False, preserve_value=False, **kw
    ):
        d = match.groupdict(default='')
        d.update(kw)

        if 'value' in d:
            key = d.pop('key', '')
            value = d['value']
        else:
            key, value = d.popitem()  # 1st one

        if not preserve_key:
            key = norm_key(key)

        fqkey = tspec(self.prefix, self.current_key, key)
        if not preserve_value:
            value = norm_val(value, fqkey)

        # spec = tspec(fqkey)

        spec = bspec(fqkey)
        assign(self.facts, spec, value, missing=dict)

    async def _interact_set_tm_attribute(
        self, match, preserve_key=False, preserve_value=False, **kw
    ):
        d = match.groupdict(default='')
        d.update(kw)

        if 'value' in d:
            key = d.pop('key', '')
            value = d['value']
        else:
            key, value = d.popitem()  # 1st one

        if not preserve_key:
            key = norm_key(key)

        fqkey = tspec(self.prefix, self.current_key, key)
        if not preserve_value:
            value = norm_val(value, fqkey)

        # spec = tspec(fqkey)

        spec = bspec(fqkey)
        assign(self.facts, spec, value, missing=dict)

    async def _interact_set_object(
        self, match, preserve_key=False, preserve_value=False, **kw
    ):
        d = match.groupdict(default='')
        d.update(kw)

        key = d.pop('key')  # must exists !

        if not preserve_key:
            key = norm_key(key)
        spec = bspec(self.prefix, self.current_key, key)

        for key, value in list(d.items()):
            if not preserve_key:
                key = norm_key(key)

            if not preserve_value:
                fqkey = tspec(self.prefix, self.current_key, key)
                value = norm_val(value, fqkey)
            d[key] = value

        assign(self.facts, spec, d, missing=dict)
        foo = 1

    async def _interact_set_tm_object(
        self, match, preserve_key=False, preserve_value=False, **kw
    ):
        d = match.groupdict(default='')
        d.update(kw)

        key = d.pop('key')  # must exists !

        if not preserve_key:
            key = norm_key(key)
        spec = bspec(self.prefix, self.current_key, key)

        for key, value in list(d.items()):
            if not preserve_key:
                key = norm_key(key)

            if not preserve_value:
                fqkey = tspec(self.prefix, self.current_key, key)
                value = norm_val(value, fqkey)
            d[key] = value

        dt = datetime.now()
        d['time'] = dt.strftime(
            '%Y-%m-%d %H:%M:%S'
        )  # TODO: include %Z for non naive TZ
        assign(self.facts, spec, d, missing=dict)

    async def _interact_indirect_set_attribute(
        self, match, preserve_key=False, preserve_value=False, **kw
    ):
        d = match.groupdict(default='')
        d.update(kw)

        value = d.pop('value')
        _key, key = d.popitem()  # 1st one

        if not preserve_key:
            key = norm_key(key)
        fqkey = tspec(self.prefix, self.current_key, key)
        if not preserve_value:
            value = norm_val(value, fqkey)

        spec = bspec(fqkey)
        assign(self.facts, spec, value, missing=dict)

    async def _interact_merge_object(
        self, match, preserve_key=False, preserve_value=False, **kw
    ):
        d = match.groupdict(default='')
        d.update(kw)

        for key, value in list(d.items()):
            if not preserve_key:
                key = norm_key(key)

            if not preserve_value:
                fqkey = tspec(self.prefix, self.current_key, key)
                value = norm_val(value, fqkey)

            d[key] = value

        spec = bspec(self.prefix, self.current_key)

        holder = glom(self.facts, spec, default={})
        value = merge(holder, d, inplace=True)
        # assign(self.facts, spec, value)
        foo = 1

    def get_spec(self, key=''):
        spec = T
        keys = self.prefix, self.current_key, key
        # spec =

        # for p in (
        # (self.prefix).split('.') + self.current_key.split('.') + [key]
        # ):

        for p in bspec(self.prefix, self.current_key, key):
            if p:
                spec = spec[p]
        return spec

    async def _interact_append_attribute(
        self, match, preserve_key=False, preserve_value=False, **kw
    ):
        d = match.groupdict(default='')
        d.update(kw)

        if 'value' in d:
            key = d.pop('key', '')
            value = d['value']
        else:
            key, value = d.popitem()  # 1st one

        key = norm_key(key)

        if not preserve_value:
            fqkey = tspec(self.prefix, self.current_key, key)
            value = norm_val(value, fqkey)

        spec = self.get_spec(key)
        try:
            value = glom(self.facts, spec) + value
        except KeyError:
            pass

        assign(self.facts, spec, value, missing=dict)
        foo = 1

    async def _enter_ready(self, *args, **kw):
        self.facts.clear()
        await super()._enter_ready()

    async def _enter_restart(self, *args, **kw):
        self.log.debug(f"Restarting GatherFact: '{self.name}'")
        await super()._enter_restart(*args, **kw)

    async def _enter_stop(self):
        # self.reactor.ctx = merge(self.reactor.ctx, self.real)
        if self.merge is None:
            self.log.debug(
                f"Ignore Merge with reactor. Data is kept in self.facts()"
            )
        else:
            ctx = self.reactor.ctx
            if self.merge in (False,):
                data = self.g(self.prefix, _target_=self.facts)
                holder = self.g(self.prefix)
                if holder is None:
                    self.s(self.prefix, data)
                elif data is not None:
                    holder.clear()
                    holder.update(data)
            else:
                merge(ctx, self.facts, inplace=True)

        await super()._enter_stop()

    def search(self, blueprint, center=[], flat=True):
        return search(self.facts, blueprint, center, flat)

    def lens(self, relativebp):
        spec = '.'.join(self.prefix)
        # blueprint = {f'.*{spec}.*.endpoint': '.*'}
        blueprint = {f'.*{spec}{k}': v for k, v in relativebp.items()}
        result = self.search(blueprint, flat=False)
        result = deindent_by(result, self.prefix)
        return result


class CPUInfoFact(GatherFact):
    """
    TBD
    """

    def __init__(self, merge=False, prefix=CPUINFO, *args, **kw):
        super().__init__(merge=merge, prefix=prefix, *args, **kw)
        self.cmdline = "cat /proc/cpuinfo"

    def _populate_interactions(self):
        super()._populate_interactions()
        self.add_interaction(
            '200_get-processor',
            r'\s*(?P<key>processor)\s+:\s+(?P<value>\d+)',
            'new_group',
        )
        self.add_interaction(
            '200_get-attribute',
            # r'\s*(?P<key>[^:]+):\s+(?P<value>[^\n]*)(\n|$)?',
            r'\s*(?P<key>[^:]+):(?P<value>.*?)(\n|$)',
            'set_attribute',
            # ctx_map={
            #'full_name': 'username',
            #'project_short_description': 'project_description',
            ##'pypi_username': 'pypi_username',
            # },
        )


class DiskInfoFact(GatherFact):
    """
    TBD
    """

    def __init__(self, merge=False, prefix=DISK_INFO, *args, **kw):
        super().__init__(merge=merge, prefix=prefix, *args, **kw)
        self.cmdline = "cat /proc/diskstats"

    def _populate_interactions(self):
        super()._populate_interactions()
        self.add_interaction(
            '200_get-disk_stats',
            r'\d+\s+\d+\s+(?P<key>\w+)\s+(?P<value>.*?)(\n|$)',
            'set_attribute',
        )


class IPInfoFact(GatherFact):
    """
    TBD
    """

    def __init__(self, merge=False, prefix=IP_INFO, *args, **kw):
        super().__init__(merge=merge, prefix=prefix, *args, **kw)
        self.cmdline = "ip a"

    def _populate_interactions(self):
        super()._populate_interactions()

        self.add_interaction(
            '200_get_ip-interface',
            # r'\s*(?P<key>processor)\s+:\s+(?P<value>\d+)',
            r'\d+:\s+(?P<value>[^:]+):\s+',
            'new_group',
        )
        self.add_interaction(
            '200_get_ip-mtu',
            r'\s*mtu\s+(?P<mtu>\d+)',
            'set_attribute',
        )
        self.add_interaction(
            '200_get_ip-state',
            r'(?imsx)\s*state\s+(?P<state>UNKNOWN|DOWN|UP)',
            'set_attribute',
        )
        self.add_interaction(
            '200_get_ip-mac',
            r'\s*link(/(?P<type>[^\s]+))?\s+(?P<mac>[0-9a-f:]+)',
            'merge_object',
        )
        self.add_interaction(
            '200_get_ip-mac-none',
            r'\s*link\s+(?P<mac>none)',
            'set_attribute',
        )
        self.add_interaction(
            '200_get_ip-inet',
            r'\s*inet\s+(?P<inet>\d+\.\d+\.\d+\.\d+/\d+)\s*',
            'set_attribute',
        )
        self.add_interaction(
            '200_get_ip-brd',
            r'\s*brd\s+(?P<brd>[^\s]+)\s*',
            'set_attribute',
        )
        self.add_interaction(
            '200_get_ip-scope',
            r'\s*scope\s+(?P<scope>host|global|link)\s*(?P<brd_dev>\w+)?\n',
            'set_attribute',
        )
        self.add_interaction(
            '200_get_ip-valid_lft',
            r'\s*valid_lft\s+(?P<valid_lft>\w+)\s*',
            'set_attribute',
        )
        self.add_interaction(
            '200_get_ip-preferred_lft',
            r'\s*preferred_lft\s+(?P<preferred_lft>\w+)\s*',
            'set_attribute',
        )


class DeviceInfoFact(GatherFact):
    """
    TBD
    """

    def __init__(self, merge=False, prefix=DEV_INFO, *args, **kw):
        super().__init__(merge=merge, prefix=prefix, *args, **kw)
        self.cmdline = "cat /proc/devices"

    def _populate_interactions(self):
        super()._populate_interactions()
        self.add_interaction(
            '200_get-device',
            r'(?imsx)\s*(?P<key>character|block)\s+devices:',
            'new_group',
        )
        self.add_interaction(
            '200_get-attribute',
            # r'\s*(?P<key>[^:]+):\s+(?P<value>[^\n]*)(\n|$)?',
            r'\s*(?P<key>\d+)\s+(?P<value>.*?)(\n|$)',
            'set_attribute',
            # ctx_map={
            #'full_name': 'username',
            #'project_short_description': 'project_description',
            ##'pypi_username': 'pypi_username',
            # },
        )


class FileContentFact(GatherFact):
    """
    TBD
    """

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.cmdline = "cat {{ name }}"
        spec = self.get_spec()
        try:
            self.old = glom(self.facts, spec)
        except KeyError:
            self.old = None
        assign(self.facts, spec, '', missing=dict)

    def _populate_interactions(self):
        super()._populate_interactions()
        self.add_interaction(
            '200_get_file_content',
            r'(?imsux)(?P<value>.*)$',
            'append_attribute',
        )


class DebRepoFact(GatherFact):
    """
    TBD
    """

    def __init__(self, merge=True, prefix=DEB_REPO_FACTS, *args, **kw):
        super().__init__(prefix=prefix, merge=merge, *args, **kw)
        self.cmdline = 'grep ^ /etc/apt/sources.list /etc/apt/sources.list.d/* | grep ":deb\s"'

    def _populate_interactions(self):
        super()._populate_interactions()
        self.add_interaction(
            '200_get_pkg-state',
            r'(?P<value>[^:]+):(?P<key>.*)(\n|$)',
            'set_attribute',
            preserve_key=True,
            preserve_value=True,
        )


class DebAddRepo(GatherFact):
    """
    TBD
    """

    def __init__(self, url, path, merge=True, prefix=DEB_FACTS, *args, **kw):
        self.url = url
        self.path = path
        super().__init__(prefix=prefix, merge=merge, *args, **kw)
        self.cmdline = 'echo -n "{{ url }}" | {{ sudo }} tee {{ path }}'

    def _populate_interactions(self):
        super()._populate_interactions()
        # self.add_interaction(
        #'200_get_pkg-state',
        # r'\s*(?P<key>[^\s]+)\s+(?P<value>.*?)(\n|$)',
        #'set_attribute',
        # )


class DebListFact(GatherFact):
    """
    TBD
    """

    def __init__(self, merge=True, prefix=DEB_FACTS, *args, **kw):
        super().__init__(prefix=prefix, merge=merge, *args, **kw)

        self.cmdline = "dpkg --get-selections"

    def _populate_interactions(self):
        super()._populate_interactions()
        self.add_interaction(
            '200_get_pkg-state',
            r'\s*(?P<key>[^\s]+)\s+(?P<value>.*?)(\n|$)',
            'set_attribute',
        )


class DebAvailableFact(GatherFact):
    """
    TBD
    """

    def __init__(
        self,
        merge=True,
        prefix=DEB_AVAILABLE_FACTS,
        upgradable=False,
        *args,
        **kw,
    ):
        super().__init__(merge=merge, prefix=prefix, *args, **kw)
        self.upgradable = upgradable
        self.cmdline = "apt list {{ '--upgradable' if upgradable else '' }}"

    def _populate_interactions(self):
        super()._populate_interactions()
        self.add_interaction(
            '200_get_pkg-state',
            # r'\s*(?P<key>[^/]+)/(?P<distro>[^\s]+)\s+(?P<version>[^\s]+)\s+(?P<platform>.*?)(\[(?P<status>installed)?(,(?P<update>automatic))?.*\])?(\n|$)',
            r'\s*(?P<key>[^/]+)/(?P<distro>[^\s]+)\s+(?P<version>[^\s]+)\s+(?P<platform>.*?)(\[(?P<status>installed)?(,(?P<update>automatic))?(upgradable\s+from:\s+(?P<old_version>.*))?.*\])?(\n|$)',
            'set_object',
        )
        self.add_interaction(
            '101_cli-warning',
            r'\s*WARNING:.*',
        )
        self.add_interaction(
            '100_cli-warning2',
            r'(?imsx)(\s*WARNING:.*?)?\bListing.*?(\n|$)',
        )


class DebUpgradableFacts(GatherFact):
    """
    TBD
    """

    def __init__(self, merge=True, prefix=DEB_AVAILABLE_FACTS, *args, **kw):
        super().__init__(merge=merge, prefix=prefix, *args, **kw)
        self.cmdline = "apt list --upgradable"

    def _populate_interactions(self):
        super()._populate_interactions()
        self.add_interaction(
            '200_get_pkg-state',
            r'\s*(?P<key>[^/]+)/(?P<distro>[^\s]+)\s+(?P<version>[^\s]+)\s+(?P<platform>.*?)(\[(?P<status>installed)?(,(?P<update>automatic))?(upgradable\s+from:\s+(?P<old_version>.*))?.*\])?(\n|$)',
            'set_object',
        )
        self.add_interaction(
            '101_cli-warning',
            r'\s*WARNING:.*',
        )
        self.add_interaction(
            '100_cli-warning2',
            r'(?imsx)(\s*WARNING:.*?)?\bListing.*?(\n|$)',
        )


class PipListFact(GatherFact):
    """
    TBD
    """

    def __init__(
        self, merge=True, prefix=PIP_FACTS, upgradable=False, *args, **kw
    ):
        super().__init__(merge=merge, prefix=prefix, *args, **kw)
        self.upgradable = upgradable
        self.cmdline = "{{ 'sudo' if sudo else '' }}  pip3 list {{ '--outdated' if upgradable else '' }} "

    def _populate_interactions(self):
        super()._populate_interactions()
        # self.prefix

        self.add_interaction(
            '200_get_pip-header',
            r'(?imsx)Package\s+Version(\s+Latest\s+Type\s+Editable\s+project)?\s*',
        )
        self.add_interaction(
            '200_get_pip-separator',
            r'-(\-|\s)+',
        )
        self.add_interaction(
            '200_get_pip-package_long',
            r"""\s*(?P<key>[a-zA-Z][^\s]+)\s+(?P<cversion>\d[^\s]+)\s+(?P<aversion>[^\s]+)\s+(?P<type>wheel|sdist|bdist)(\s+(?P<path>[^\s]+))?(\n|$)""",
            'set_object',
        )
        self.add_interaction(
            '200_get_pip-package_short',
            r"""\s*(?P<key>[a-zA-Z][^\s]+)\s+(?P<cversion>\d[^\s]+)(\s+(?P<path>[^\s]+))?(\n|$)""",
            'set_object',
        )
