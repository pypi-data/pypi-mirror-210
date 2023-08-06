import time
import yaml
import semver

from glom import glom

from .definitions import PIP_FACTS

from .shell import (
    bspec,
    Finder,
)

from .action import Action
from .agent import Agent
from .service import (
    AddSudoers,
    ChangeLocale,
    SystemUnitStart,
    SystemdDaemonReload,
)
from .scanner import Settler
from .watch import WatchDog
from .wireguard import WireGuard

SERVICE_TEMPLATE = """
# pastor.service
[Unit]
Description=Agent that supervise and reacts to issues for keeping the basic node operative running
Wants=network-online.target
After=network-online.target

[Service]
Environment="WINGHOME=True"
Environment="WINGDB_HOSTPORT=10.220.2.200"

WorkingDirectory=/home/%i/workspace/iot
#ExecStart=iot plan apply --output true user:123456@localhost
ExecStart=./debug.sh
User=%i
Group=%i
Restart=always
RestartSec=60

[Install]
WantedBy=multi-user.target
"""


class AsService(Action):
    """
    - [ ] select runing by user or system
    """

    def __init__(self, *args, **kw):
        self._stop_no_seq = False  # wait until fibers have done
        super().__init__(*args, **kw)
        foo = 1

    # --------------------------------------------------
    # Coded as sequence: # TODO: review
    # --------------------------------------------------
    async def _seq_10_service_unit(self, *args, **kw):
        path = '/etc/systemd/system/pastor@.service'
        content = self.expand(SERVICE_TEMPLATE)
        attributes = {
            'group': 'root',
            'owner': 'root',
            'mode': '0644',
        }
        result = await self.create_file(path, content=content, **attributes)

        return result

    async def _seq_20_service_enable(self, *args, **kw):
        name = 'pastor@user.service'
        enable = True

        service = self.new_action(SystemUnitStart, name=name, enable=enable)
        result = await self.wait(service)
        return not any(result)

    async def _seq_30_service_reload(self, *args, **kw):
        service = self.new_action(SystemdDaemonReload)
        result = await self.wait(service)
        return not any(result)

    async def _seq_99_service_ends(self, *args, **kw):
        return True


class Installer(Agent):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.target = {}

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
                #'klass': AddSudoers,
            },
            {
                #'klass': ChangeLocale,
            },
            {
                #'klass': Settler,
                'daemon': False,
            },
            {
                'klass': AsService,
            },
            # {
            #'klass': WatchDog,
            # },
            # {
            #'klass': WireGuard,
            # },
        ]

        # initial launch
        for action in real:
            self.log.debug(f"Launching: {action}")
            if 'klass' in action:
                self.new_action(**action)
                await self.sleep()

        self.log.info(f"All bootstrap ({len(real)}) actions fired.")

        foo = 1

    # --------------------------------------------------
    # Domestic Fibers
    # --------------------------------------------------
