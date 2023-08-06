import time
import yaml
import semver

from glom import glom

from .definitions import PIP_FACTS

from .shell import (
    bspec,
    Finder,
)

from .agent import Agent
from .service import AddSudoers, ChangeLocale
from .scanner import Settler
from .watch import WatchDog
from .wireguard import WireGuard


class Pastor(Agent):
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
                'klass': AddSudoers,
            },
            {
                #'klass': ChangeLocale,
            },
            {
                'klass': Settler,
            },
            {
                'klass': WatchDog,
            },
            {
                'klass': WireGuard,
            },
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
