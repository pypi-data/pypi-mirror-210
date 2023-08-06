# ------------------------------------------------
# Misc
# ------------------------------------------------
DEFAULT_EXECUTOR = 'default_executor'
DEFAULT_CONNECTION = '_default_connection'
ANY_CATEGORY = 'any_category'


# ------------------------------------------------
# Pkg Verions
# ------------------------------------------------
LASTEST = 'lastest'
INSTALL = 'install'
DEINSTALL = 'deinstall'
UNINSTALL = 'uninstall'
NEEDS_INSTALL = (INSTALL, LASTEST)
NEEDS_UNINSTALL = (DEINSTALL, UNINSTALL)

# ------------------------------------------------
# xxx
# ------------------------------------------------
REPO_PREFERENCES = 'etc', 'pkg', 'repo', 'preferences'
T_TPL_LOCATION = 'etc', 'templates', 'locations'


# ------------------------------------------------
# FACTS
# ------------------------------------------------
WORLD = ('_world',)
REAL = ('real',)
AVAILABLE = ('_available',)
TARGET = ('target',)
SYS = ('sys',)

PACKAGES = ('pkg',)

RUN = REAL + ('_run',)

CPUINFO = REAL + SYS + ('cpuinfo',)
DEV_INFO = REAL + SYS + ('devices',)
DISK_INFO = REAL + SYS + ('disks',)
IP_INFO = REAL + SYS + ('ip',)


TPL_LOCATION = TARGET + T_TPL_LOCATION

VAR = ('var',)
PKG_FACTS = VAR + PACKAGES

ETC = ('etc',)
TEMP = ('tmp',)
ENV = ('env',)

UNITS = ('units',)
# ------------------------------------------------
# Packages
# -----------------------------------------------
DEB = ('deb',)
DEB_FACTS = REAL + PKG_FACTS + DEB
DEB_AVAILABLE_FACTS = WORLD + AVAILABLE + PKG_FACTS + DEB

DEB_REPO_FACTS = REAL + ETC + PACKAGES + DEB

PIP = ('pip',)
PIP_FACTS = REAL + PKG_FACTS + PIP

FILE_FACTS = VAR + ('fs',)

DEB_AVAILABLE = PKG_FACTS + DEB

DEB_INSTALLED = PKG_FACTS + ('installed',) + DEB
DEB_INSTALLED_FACTS = REAL + DEB_INSTALLED


# ------------------------------------------------
# Service
# -----------------------------------------------
SERVICES = ('services',)
SERVICE_FACTS = VAR + SERVICES

SERVICE_STATUS_FACTS = REAL + SERVICE_FACTS


FS_FACTS = REAL + FILE_FACTS

# ------------------------------------------------
# network
# ------------------------------------------------
NET = ('net',)
NETWORK_FACTS = REAL + VAR + NET

DNS = ('dns',)
DNS_FACTS = NETWORK_FACTS + DNS

PING = ('ping',)
PING_FACTS = NETWORK_FACTS + PING

WIREGUARD = ('wg',)

WIREGUARD_FACTS = NETWORK_FACTS + WIREGUARD
WIREGUARD_ETC = WIREGUARD_FACTS[:1] + ETC + WIREGUARD_FACTS[2:]


# ------------------------------------------------
# var
# ------------------------------------------------
VAR_STATUS = 'var', 'status'

# ------------------------------------------------
# locale
# ------------------------------------------------
LOCALE_PREFERENCES = 'etc', 'default', 'locale'
REAL_LOCALE_PREFERENCES = REAL + LOCALE_PREFERENCES


# ------------------------------------------------
# reboot
# ------------------------------------------------
REBOOT = ('reboot',)
REBOOT_FACTS = REAL + VAR + REBOOT

# ------------------------------------------------
# modem
# ------------------------------------------------
MODEM = ('modem',)
MODEM_FACTS = NETWORK_FACTS + MODEM
MODEM_ID_FACTS = MODEM_FACTS + ('modem_id',)
MODEM_FACTS_SUBSET = MODEM_FACTS + (
    r'\d+',
    '(status|general|system)',
    '(state|modem_id|.*port)',
)

# ------------------------------------------------
# network manager
# ------------------------------------------------
CONNECTION_STATUS = NETWORK_FACTS + ('connection',)
DEVICE_STATUS = NETWORK_FACTS + ('device',)

# ------------------------------------------------
# glom extensions
# ------------------------------------------------
from glom import glom, assign


def setdefault(obj, path, val, missing=dict):
    current = glom(obj, path, default=None)
    if current is None:
        assign(obj, path, val, missing=missing)
        return val
    return current
