import sys
import os
import inspect
import time

sys.path.append(os.path.abspath('.'))

from .definitions import (
    DEB_FACTS,
    REAL,
    TARGET,
    PIP_FACTS,
    SERVICE_FACTS,
    setdefault,
    DEFAULT_EXECUTOR,
)

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
)

from .action import Action

# from .ssh import ShellSTM


class Agent(Action):
    """STM alike daemon
    WIP
    """

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
