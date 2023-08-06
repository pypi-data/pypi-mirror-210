import time
import yaml
import semver

from glom import glom, assign

from pycelium.tools.containers import (
    simplify,
    merge,
    option_match,
    gather_values,
)

from .definitions import (
    PIP_FACTS,
    MODEM_FACTS,
    MODEM_ID_FACTS,
    CONNECTION_STATUS,
    DEVICE_STATUS,
    REAL,
    TARGET,
    ETC,
)

from .shell import (
    bspec,
    Finder,
)

from .action import Action
from .agent import Agent
from .service import Service
from .gathering import GatherFact


class FindModem(GatherFact):
    """
    TBD
    """

    def __init__(self, merge=None, prefix=MODEM_FACTS, *args, **kw):
        "Find modem id, but don't merge data into reactor"
        super().__init__(merge=merge, prefix=prefix, *args, **kw)
        self.cmdline = "mmcli -L"

    def _populate_interactions(self):
        super()._populate_interactions()
        self.add_interaction(
            '200_get-modem',
            """(?imsux)
            /org/freedesktop/ModemManager\d+/Modem/(?P<modem_id>\d+).*?(\n|$)
            """,
            'set_attribute',
        )


class NetworkManagerDeviceFacts(GatherFact):
    """
    TBD
    """

    SAMPLE = """
    """

    def __init__(self, merge=False, prefix=DEVICE_STATUS, *args, **kw):
        super().__init__(merge=merge, prefix=prefix, *args, **kw)
        self.cmdline = "nmcli device show"

    def _populate_interactions(self):
        super()._populate_interactions()
        self.add_interaction(
            '200_get-device',
            r'\s*GENERAL.DEVICE:\s+(?P<key>[^\n\s]+)(\n|$)',
            'new_group',
        )
        self.add_interaction(
            '205_get-attribute',
            # r'\s*(?P<key>[^:]+):\s+(?P<value>[^\n]*)(\n|$)?',
            r'\s*(?P<key>[^:]+):(?P<value>.*?)(\n|$)',
            'set_attribute',
            # ctx_map={
            #'full_name': 'username',
            #'project_short_description': 'project_description',
            ##'pypi_username': 'pypi_username',
            # },
        )


class NetworkManagerConnectionFacts(GatherFact):
    """
    TBD
    """

    SAMPLE = """
    NAME            UUID                                  TYPE  DEVICE
    gsm-connection  d81fd29d-a3ce-458f-bf85-e01d9790f331  gsm   cdc-wdm0
    CIBERNOS3       9f880d8f-910b-4933-9a4c-b9ce99e7e0d5  wifi  --
    CIBERNOS3 1     79830e7c-8250-4d9e-8c30-b305c34b4b30  wifi  --
    OPPOJL          451ae80a-0e24-4966-87a5-ea0465023a70  wifi  --
    RAK_187         dfa9b748-b02d-4ed6-84d0-695ee4e987b5  wifi  --
    """

    def __init__(self, merge=False, prefix=CONNECTION_STATUS, *args, **kw):
        super().__init__(merge=merge, prefix=prefix, *args, **kw)
        self.cmdline = "nmcli connection show"

    def _populate_interactions(self):
        super()._populate_interactions()
        self.add_interaction(
            '100_header-modem',
            r"""(?imsx)
                       NAME
                       \s+
                       UUID
                       \s+
                       TYPE
                       \s+
                       DEVICE
                    """,
        )

        self.add_interaction(
            '200_get-nm_connection',
            r"""(?sx)
            (?P<connection_name>[\w\-]+)
            \s+
            (?P<key>[a-f0-9\-]+)  # uuid
            \s+
            # TODO: add any other type, but try to avoid [\w\-]+ to match only this response type
            (?P<type>wifi|tun|bridge|wireguard|gsm)
            \s+
            (?P<device>[\w\-]+)
            """,
            'set_object',
        )


MODEM_KEY_ID = 'equipment_id'


class SingleModemFact(GatherFact):
    """
    TBD
    """

    def __init__(
        self, modem_id=0, merge=True, prefix=MODEM_FACTS, *args, **kw
    ):
        super().__init__(merge=merge, prefix=prefix, *args, **kw)
        self.modem_id = modem_id
        self.cmdline = "mmcli --modem={{ modem_id }}"

    def _populate_interactions(self):
        super()._populate_interactions()
        self.add_interaction(
            '200_get-group',
            r'\n\s+(?P<key>[^\s\|]+)\s+\|',
            'new_group',
        )
        self.add_interaction(
            '200_get-parameter',
            r'\s+(?P<key>[^:\|]+):\s(?P<value>.*?)(\n|$)',
            'set_attribute',
        )

        self.add_interaction(
            '500_modem_not_found',
            r'error.*couldn.*find.*modem.*$',
        )

    async def _enter_stop(self):
        spec = '.'.join(MODEM_FACTS)
        blueprint = {f'.*{spec}': '.*'}
        result = self.search(blueprint, flat=False)
        result = simplify(result)
        assign(result, 'general.modem_id', self.modem_id, missing=dict)

        blueprint = {f'.*{MODEM_KEY_ID}': '.*'}
        mid = self.search(blueprint, flat=False)
        mid = simplify(mid)
        if mid:
            _, mid = mid.popitem()

            spec = bspec(MODEM_FACTS, mid)
            self.facts.clear()
            assign(self.facts, spec, result, missing=dict)
        else:
            self.log.error(
                f"Unable to get modem id: using key: '{MODEM_KEY_ID}'. Modem can't not be configured!"
            )

        # self.ctx.update(result)
        # self.primary_port = self.g(MODEM_FACTS, 'system', 'primary_port')

        await super()._enter_stop()


class ModemAction(Action):
    """
     mmcli --help-modem
    -e, --enable       Enable a given modem
    -d, --disable      Disable a given modem
        --inhibit      Inhibit the modem
    -r, --reset        Reset a given modem

    """

    def __init__(self, modem_id, *args, **kw):
        super().__init__(*args, **kw)
        self.modem_id = modem_id
        # self.cmdline ="sudo mmcli --modem={{ modem_id }} --simple-connect=apn={{ apn_name }},ip-type=ipv4v6",

    def _populate_interactions(self):
        super()._populate_interactions()
        self.add_interaction(
            '200_ok_response',
            f"""(?imsx)
            .*?(?P<result>successfully\s+(enabled|connected|added|deleted).*)
            """,
            #'default_response',
            # answer='yes',
        )


class ModemDisablePin(ModemAction):
    def __init__(self, pin, sim_id=0, enable=True, sudo=True, *args, **kw):
        super().__init__(sudo=sudo, *args, **kw)
        self.pin = pin
        self.sim_id = sim_id
        self.enable = enable
        self.cmdline = "mmcli -i {{ sim_id}} --pin {{ pin }} --disable-pin"


class ModemEnable(ModemAction):
    def __init__(self, enable=True, sudo=True, *args, **kw):
        super().__init__(sudo=sudo, *args, **kw)
        self.enable = enable
        self.cmdline = "mmcli --modem={{ modem_id }} {{ '--enable' if enable else '--disable' }}"


class APNCreation(ModemAction):
    def __init__(self, apn_name=None, sudo=True, *args, **kw):
        super().__init__(sudo=sudo, *args, **kw)
        self.apn_name = apn_name
        self.cmdline = "mmcli --modem={{ modem_id }} --simple-connect='apn={{ apn_name }},ip-type=ipv4v6'"


class NetworkManagerAction(Action):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        # self.cmdline ="sudo mmcli --modem={{ modem_id }} --simple-connect=apn={{ apn_name }},ip-type=ipv4v6",

    def _populate_interactions(self):
        super()._populate_interactions()
        self.add_interaction(
            '200_ok_response',
            f"""(?imsx)
            .*?(?P<result>successfully\s+(enabled|connected|added|deleted).*)
            """,
            #'default_response',
            # answer='yes',
        )


class GSMConnectionCreation(NetworkManagerAction):
    def __init__(
        self,
        primary_port=None,
        connection_name=None,
        operator_name=None,
        sudo=True,
        *args,
        **kw,
    ):
        self.primary_port = primary_port
        self.connection_name = connection_name
        self.operator_name = operator_name
        super().__init__(sudo=sudo, *args, **kw)

        self.cmdline = "nmcli connection add type gsm ifname {{ primary_port }} con-name {{ connection_name }} apn {{ apn_name }}"


class ConnectionDelete(NetworkManagerAction):
    def __init__(
        self,
        uuid,
        sudo=True,
        *args,
        **kw,
    ):
        self.uuid = uuid
        super().__init__(sudo=sudo, *args, **kw)

        self.cmdline = "nmcli connection delete uuid {{ uuid }}"


class ConnectionRename(NetworkManagerAction):
    def __init__(
        self,
        uuid,
        connection_name,
        sudo=True,
        *args,
        **kw,
    ):
        self.uuid = uuid
        self.connection_name = connection_name
        super().__init__(sudo=sudo, *args, **kw)

        self.cmdline = "nmcli connection modify uuid {{ uuid }} con-name {{ connection_name }}"


class RadioAction(Action):
    def __init__(
        self,
        sudo=True,
        *args,
        **kw,
    ):
        super().__init__(sudo=sudo, *args, **kw)

        self.cmdline = "nmcli radio wwan on"


class ModemConfigurator(GatherFact):
    """

    Actions:
    modem.power_state:
      - off: ---> on: sudo mmcli --modem=0 --set-power-state-on


    modem.state:
      - disabled: ---> enable: sudo mmcli --modem=0 --enable
      -


    - [x] Get Modem HW info, modem, device,state (registered, etc), operator name: SingleModemFact
    - [x] Connect Modem to the Mobile Network using associated device
    - [x] Get Network config: NetworkManagerConnectionFacts
    - [x] Find the 'gsm' connection and finish its as we expect
      - [x] rename if needed
      - [x] delete duplicated ones
      - [ ]


    """

    CONNECTION_NAME = 'gsm-connection'

    def __init__(
        self, connection_name=None, prefix=MODEM_FACTS, *args, **kw
    ):
        super().__init__(prefix=prefix, *args, **kw)
        # self._stop_no_seq = False

        self.connection_name = connection_name or self.CONNECTION_NAME

        # TODO: load operator from config yaml file
        self.ctx['APN'] = {
            '.*orange.*': 'orangeworld',
            '.*movistar.*': 'Movistar',
            '.*vodafone.*': 'Vodafone',
        }
        self.modem_id = 'unknown_modem_id'
        self.modem_uid = 'unknown_modem_uid'
        self.prefix2 = ''

    # --------------------------------------------------
    # Domestic Fibers
    # --------------------------------------------------

    async def _seq_03_config_wwan(self, *args, **kw):
        while self.running:
            executor = await self.is_connected()
            if executor:
                # activate radio
                action = self.new_action(RadioAction)
                result = await self.wait(action)
                return True

    async def _seq_05_config_find(self, *args, **kw):
        # TODO: Extract all modeml availables
        klass = SingleModemFact
        action = self.new_action(FindModem)
        result = await self.wait(action)
        self.modem_id = self.g(
            action.prefix, 'modem_id', _target_=action.facts
        )
        if self.modem_id:
            self.log.info(f"Found modem_id={self.modem_id}, launch {klass}")
            action = self.new_action(
                klass, modem_id=self.modem_id, restart=-1
            )
            result = await self.wait(action)
            if not any(result):
                specs = {
                    MODEM_KEY_ID: '\d+',
                }
                # ctx = self.gather_values(self.prefix, **specs)
                ctx = gather_values(action.facts, **specs)
                self.modem_uid = ctx.get(MODEM_KEY_ID)
                self.prefix2 = self.prefix + (self.modem_uid,)
                return not any(result)  # True
        foo = 1

    async def _seq_10_config_mmifacts(self, *args, **kw):
        specs = {
            'modem_id': '\d+',
            '.*operator.*': None,
            'primary_port': None,
            '.*status.*state.*': None,
        }
        ctx = self.gather_values(self.prefix2, **specs)
        self.ctx.update(ctx)
        return 'state' in ctx

        # for name in specs:
        # if not option_match(name, *ctx):
        # self.log.error(
        # f"can't find {name} from modem: {self.prefix}"
        # )
        # return False

        # return True

    async def _seq_17_config_signaling(self, *args, **kw):
        """Wait for modem to connect to operator"""
        klass = SingleModemFact

        while self.running:
            state = self.ctx.get('state', 'unknown')

            if option_match(state, 'locked'):
                self.log.warning(
                    f"SIM Card is Locked. Trying remove PIN: {self.prefix2}"
                )
                # try to the PIN
                # TODO: Future, config multiples IMEI gsm modules
                specs = {
                    '.*pin.*': None,
                }
                # find 'connection_name' in target state or use default
                target = self.gather_values(
                    TARGET + ETC + self.prefix[2:], **specs
                )
                pin = target.get('pin')
                if pin:
                    self.log.warning(f"Using PIN: {pin} for {self.prefix2}")
                    enable = self.new_action(
                        ModemDisablePin, pin=pin, **self.ctx
                    )
                    result = await self.wait(enable)
                    for line in enable.history:
                        self.log.info(line)
                else:
                    self.log.warning(
                        f"PIN is not provided, neither YAML files of CLI arguments"
                    )

            elif option_match(state, 'disabled'):
                self.log.info(
                    f"Modem dissabled. Trying to enable: {self.prefix2}"
                )
                enable = self.new_action(ModemEnable, **self.ctx)
                result = await self.wait(enable)

            # elif option_match(state, 'registered'):
            ## enable = self.new_action(ModemEnable, **self.ctx)
            ## result = await self.wait(enable)

            # self.log.info(
            # f"Waiting for signaling ending: {self.prefix2} ... and get 'connected' status"
            # )

            elif option_match(state, 'registered|connected'):
                self.log.info(f"Modem signaling is ok: {self.prefix2}")
                return True
            else:
                self.log.warning(
                    f"State: '{state}' is not handler...please review in code"
                )

            await self.sleep()
            action = self.new_action(
                klass, modem_id=self.modem_id, restart=-1, _warm_body=0
            )
            result = await self.wait(action)

            # try to select operator from target YAML
            # othewise use default order

    async def _seq_20_config_apn(self, *args, **kw):
        """Try to config modem APN using all known Network Operators
        Note: is asummed PIN is disabled

        Note: It looks like is safe to try to configure an APN with
              another operator name. It'll simply fail.
              Is algo possible to try to configure an already APN with
              same values. Returns Ok.

              So we can use any of these options:
              - blindly try to configure all known APN
              - check the operator name and use just the right one
        """

        # find if there is an active connection using the
        # modem port
        while self.running:
            await self.sleep()
            action = self.new_action(NetworkManagerDeviceFacts)
            result = await self.wait(action)
            if any(result):
                self.show_problem(action)
                continue
            primary_port = self.ctx.get('primary_port')
            dev_info = self.g(action.prefix, primary_port)
            # specs = {
            #'.*general.*': None,
            # }
            # dev_info = self.gather_values(action.prefix, primary_port, **specs)

            # compare operator with desired target state
            # prefix = list(self.prefix)
            # prefix[0] = TARGET
            # ctx = self.gather_values(prefix, **specs)
            #  some checks
            VALID_DEV_TYPES = ('gsm',)
            if dev_info.get('general.type') not in VALID_DEV_TYPES:
                self.log.error(
                    f"device {primary_port} is not in {VALID_DEV_TYPES}"
                )
                return False

            # gsm device is configured?
            # if not dev_info.get('ip4.gateway'):

            state = self.ctx.get('state', 'unknown')
            if option_match(state, 'registered|connected'):
                # try to select the operator or test all known operators
                operator_name = self.ctx.get('operator_name', '.*')
                apn_list = []
                for patt, apn in self.ctx['APN'].items():
                    if option_match(operator_name, patt):
                        apn_list.append(apn)

                for apn_name in apn_list:
                    action = self.new_action(
                        APNCreation, apn_name=apn_name, **self.ctx
                    )
                    result = await self.wait(action)
                    if not any(result):
                        self.log.info(
                            f"Register modem {self.prefix} into {apn_name} mobile network"
                        )
                        self.ctx['apn_name'] = apn_name

                        break
                else:
                    self.log.error(
                        f"Can't register into any mobile network operator!!, let's try to continue"
                    )
                    # return False

                # TODO: add some check to see modem is properly cnfigured
            # elif option_match(state, 'connected'):
            # self.log.debug(f"Modem: {self.prefix} already connected")
            else:
                self.log.warning(
                    f"Modem: {self.prefix} state: {state} is not handled!"
                )

            return True

    async def _seq_40_config_unique(self, *args, **kw):
        """
        Only must be a single connection for
        nmcli connection show
        NAME            UUID                                  TYPE  DEVICE
        gsm-connection  f02c91e3-8da7-4a4c-8b0f-1be9cf41b7be  gsm   cdc-wdm0
        gsm-connection  fb2510aa-b8c2-4f93-9587-dca37bea340b  gsm   --

        Remove any duplicate connection (is exists)
        Keep wifi connection intacts
        TODO: use a configuration file as POLICY, not hardcoded
        """
        while self.running:
            # TODO: Future, config multiples IMEI gsm modules
            specs = {
                '.*connection_name.*': None,
            }
            # find 'connection_name' in target state or use default
            target = self.gather_values(TARGET + self.prefix[1:], **specs)
            self.connection_name = target.get(
                'connection_name', self.connection_name
            )

            action = self.new_action(NetworkManagerConnectionFacts)
            result = await self.wait(action)

            primary_port = self.ctx.get('primary_port')

            VALID_GSM = ('gsm',)
            DEV_DISABLED = ('--', '')
            connections = self.g(action.prefix) or {}
            for uuid, info in connections.items():
                device = info.get('device')
                con_name = info.get('connection_name')
                type_ = info.get('type')
                if device == primary_port:
                    if type_ not in VALID_GSM:
                        self.log.error(f"{uuid} is not {VALID_GSM}??")
                        continue
                    if con_name in (self.connection_name,):
                        self.log.debug(
                            f"ok, found {uuid} named '{con_name}' connected to '{primary_port}'"
                        )
                    else:
                        self.log.debug(
                            f"ok, found {uuid} named '{con_name}' connected to '{primary_port}' but name does not match '{self.connection_name}'"
                        )
                        self.log.debug(
                            f"renaming connection {uuid}: {con_name} --> {self.connection_name}"
                        )
                        action = self.new_action(
                            ConnectionRename,
                            uuid=uuid,
                            connection_name=self.connection_name,
                        )
                        result = await self.wait(action)
                elif device in DEV_DISABLED:
                    if type_ in VALID_GSM:
                        self.log.warning(
                            f'removing duplicated connection: {uuid} info: {info}'
                        )
                        action = self.new_action(ConnectionDelete, uuid=uuid)
                        result = await self.wait(action)
                    else:
                        self.log.debug(
                            f"preserving connection: {uuid} info {info}"
                        )
            return True

    async def _seq_50_config_device(self, *args, **kw):
        action = self.new_action(NetworkManagerDeviceFacts)
        result = await self.wait(action)
        primary_port = self.ctx.get('primary_port')
        dev_info = self.g(action.prefix, primary_port)

        # real state
        real = self.g(self.prefix2)
        # TODO: Future, config multiples IMEI gsm modules
        specs = {
            '.*connection_name.*': None,
        }
        # find 'connection_name' in target state or use default
        target = self.gather_values(TARGET + self.prefix[1:], **specs)
        self.connection_name = target.get(
            'connection_name', self.connection_name
        )

        if dev_info.get('general.connection') in ('--', ''):
            # it's looks like isn't configure yet any nmcli connection
            action = self.new_action(
                GSMConnectionCreation,
                connection_name=self.connection_name,
                # primary_port=self.primary_port,
                # operator_name=self.operator_name,
                **self.ctx,
            )
            result = await self.wait(action)
            if not any(result):
                self.log.info(
                    "Register modem {modem_id} into {apn_name} mobile network".format_map(
                        self.ctx
                    )
                )

                return True

        # TODO: add some check to see modem is properly cnfigured
        return True

    async def _seq_90_config_copy(self, *args, **kw):
        """Copy connection name from device to modem space, so
        GAP presumably will be closed.
        """
        # find 'connection_name' in target state or use default
        # TODO: Future, config multiples IMEI gsm modules
        specs = {
            '.*connection_name.*': None,
        }
        target = self.gather_values(TARGET + self.prefix[1:], **specs)
        self.connection_name = target.get(
            'connection_name', self.connection_name
        )

        action = self.new_action(NetworkManagerDeviceFacts)
        result = await self.wait(action)
        primary_port = self.ctx.get('primary_port')
        dev_info = self.g(action.prefix, primary_port)

        dev_con_name = dev_info.get('general.connection')

        self.s((self.prefix2, 'connection_name'), dev_con_name)

        foo = 1

    async def _seq_99_config_end(self, *args, **kw):
        self.log.info("end")
        foo = 1


class ModemConfigAPN(GatherFact):
    pass


class ModemFacts(GatherFact):
    """Find modem an then launch a SingleModeFact.

    Implementes as sequence fibers
    Do not get data by itself (merge=None)
    """

    def __init__(self, prefix=MODEM_FACTS, *args, **kw):
        super().__init__(prefix=prefix, *args, **kw)

    # --------------------------------------------------
    # Bootstraping
    # --------------------------------------------------

    # --------------------------------------------------
    # Domestic Fibers
    # --------------------------------------------------
    async def _seq_10_facts_get(self, *args, **kw):
        # TODO: Extract all modeml availables
        klass = SingleModemFact
        action = self.new_action(FindModem)
        result = await self.wait(action)
        modem_id = self.g(action.prefix, 'modem_id', _target_=action.facts)
        if modem_id:
            self.log.info(f"Found modem_id={modem_id}, launch {klass}")
            action = self.new_action(klass, modem_id=modem_id, restart=-1)
            result = await self.wait(action)
            return not any(result)
        foo = 1
