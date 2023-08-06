import sys
import os

from glom import glom

sys.path.append(os.path.abspath('.'))

from .definitions import (
    SERVICE_FACTS,
)
from glom import assign
from .tools.containers import bspec
from .service import Service


class Grafana(Service):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        # self.FACT_PREFIX['real.etc.grafana'] = {}
        # self.TEMPLATES['grafana.conf.j2'] = {
        #'dest': '/etc/wireguard/{{ item }}.conf',
        #'owner': 'root',
        #'mode': 0o600,
        #'user_service': False,
        # }

        # deb packages
        # self._add_package_dependence('grafana')
