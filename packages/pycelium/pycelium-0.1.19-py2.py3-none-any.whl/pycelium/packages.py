import sys
import os
import re
import hashlib
import random
import inspect
import shutil

sys.path.append(os.path.abspath('.'))

from .definitions import (
    DEB,
    DEB_FACTS,
    REAL,
    TARGET,
    PIP_FACTS,
    SERVICE_FACTS,
    setdefault,
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
)

from .action import Action


class PkgInstall(Action):
    HANDLES = tuple()

    def __init__(self, install=True, upgrade=False, *args, **kw):
        super().__init__(*args, **kw)
        self.install = install
        self.upgrade = upgrade


class DebPkgInstall(PkgInstall):
    """
    Install .deb packages using apt
    """

    HANDLES = DEB

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.cmdline = "{{ 'sudo ' if sudo else '' }}apt-get -o DPkg::Lock::Timeout=600 {{ 'install' if install else 'remove' }} {{ name }}"

        # shared with DebAptUpdate
        self.add_interaction(
            '200_get_repo_url',
            r'(?P<action>Hit|Get|Ign):(?P<seq>\d+)\s+(?P<url>[^\s]+).*?(\n|$)',
            #'set_object',
        )
        # (Reading database ... 35%
        # self.add_interaction(
        #'201_reading_db',
        # r'.*?Reading\s+database\.*?\d+\%(\n|$)',
        ##'set_object',
        # )
        self.add_interaction(
            '202_regular_activity',
            r'(?P<action>Reading|Preparing|Unpacking|Selecting|Setting|Processing).*(\n|$)',
            #'set_object',
        )
        self.add_interaction(
            '203_restarting_service',
            r'Restarting.*?(?P<service>\w+).*service.*?(?P<status>\w+)(\n|$)',
            #'set_object',
        )
        # 0 upgraded, 0 newly installed, 0 to remove and 323 not upgraded.
        self.add_interaction(
            '204_summary',
            r'(?P<upgraded>\d+)\s+upgraded.*?(?P<new>\d+).*?newly.*?(?P<removed>\d+).*?remove.*?(?P<not_upgraded>\d+).*',
            #'set_object',
        )


class PipPkgInstall(PkgInstall):
    """
    Install pip packages
    """

    HANDLES = tuple(['pip'])

    def __init__(self, upgrade=True, *args, **kw):
        super().__init__(*args, **kw)
        self.upgrade = update
        self.cmdline = "{{ 'sudo' if sudo else '' }} pip3 {{ 'install' if install else 'uninstall' }} {{ '-U' if install and upgrade else '' }} {{ name }}"

    def _populate_interactions(self):
        super()._populate_interactions()
        self.add_interaction(
            '300_already_satisfied',
            r'.*\s+already\s+satisfied:\s+(?P<already>[^\s]+).*?(\n|$)',
            #'default_response',
            # answer='yes',
        )


class DebRepository(Action):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.cmdline = "{{ 'sudo' if sudo else '' }} pip3 {{ 'install' if install else 'uninstall' }} {{ '-U' if upgrade else '' }} {{ name }}"

    def _populate_interactions(self):
        super()._populate_interactions()
        self.add_interaction(
            '300_already_satisfied',
            r'.*\s+already\s+satisfied:\s+(?P<already>[^\s]+).*?(\n|$)',
            #'default_response',
            # answer='yes',
        )


def test_deb_packages():
    from asyncio import run, wait, create_task, sleep, FIRST_COMPLETED, Queue
    from .shell import Reactor, DefaultExecutor

    reactor = Reactor()

    conn = DefaultExecutor()
    reactor.attach(conn)

    # stm = CoockieCutter()
    packages = 'python3-selenium yorick-svipc python3-okasha raysession python3-ulmo'
    for name in packages.split():
        stm = DebPkgInstall(name=name)
        reactor.attach(stm)

    run(reactor.main())
    foo = 1
    reactor = Reactor()

    conn = DefaultExecutor()
    reactor.attach(conn)
    for name in packages.split():
        stm = DebPkgInstall(name=name, install=False)
        reactor.attach(stm)

    run(reactor.main())
    foo = 1


def test_pip_packages():
    from asyncio import run, wait, create_task, sleep, FIRST_COMPLETED, Queue
    from .shell import Reactor, DefaultExecutor

    reactor = Reactor()

    conn = DefaultExecutor()
    reactor.attach(conn)

    # stm = CoockieCutter()
    packages = 'ppci voronoiville python-calamine'
    # packages = 'python-calamine'
    for name in packages.split():
        stm = PipPkgInstall(name=name)
        reactor.attach(stm)

    run(reactor.main())
    foo = 1
    reactor = Reactor()

    conn = DefaultExecutor()
    reactor.attach(conn)
    for name in packages.split():
        stm = PipPkgInstall(name=name, install=False)
        reactor.attach(stm)

    run(reactor.main())
    foo = 1
