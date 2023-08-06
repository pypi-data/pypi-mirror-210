#!/usr/bin/env python3
"""
- [ ] load configuration from yaml
- [ ] monitorize FS for plugings and config files reloading
- [x] main entry point
- [ ] cleaning test files
- [ ] split plugin files


"""
import re
import sys
import os
import random
import time

import asyncio_mqtt as aiomqtt
import paho.mqtt as mqtt

# sys.path.append(os.path.abspath('.'))
# import wingdbstub
from .shell import Agent, Reactor, run, sleep


# A simple 3g modem monitor
class Modem(Agent):
    # TODO: use jinja2 as template render engine
    FIND_MODEM = 'find_modem'
    GET_MODEM_INFO = 'get_modem_info'

    FIND_CDC = 'find_cdc'
    # GET_CDC_INFO = 'get_cdc_info'

    MODEM_OPTION = 'enable_modem'
    APN_CONNECT = 'apn_connect'

    GET_CDC_WDM_INTERFACE = 'get_cdc_wdm'
    GET_NM_CONNECTIONS = 'get_nm_connections'
    GET_NM_CONNECTIONS_PARAM_BY_UUID = 'get_nm_connections_params_by_uuid'
    ADD_GSM_CONNECTION = 'add_gsm_connection'
    RENAME_GSM_CONNECTION = 'rename_gsm_connection'
    DEL_GSM_CONNECTION_BY_NAME = 'del_gsm_connection_by_name'
    DEL_GSM_CONNECTION_BY_UUID = 'del_gsm_connection_by_uuid'
    UPDATE_METRIC_GSM_CONNECTION_BY_UUID = (
        'update_metric_gsm_connection_by_name'
    )
    UP_GSM_CONNECTION_BY_NAME = 'up_gsm_connection'
    UP_GSM_CONNECTION_BY_UUID = 'up_gsm_connection_by_uuid'

    def __init__(self, name='modem', *args, **kw):
        super().__init__(name=name, *args, **kw)

        self._modem_info = {}

        # TODO: load from config file and use built-in values as default

        # TODO: load operator from config yaml file
        self.ctx['APN'] = [
            'Movistar',
            'orangeworld',
            'Vodafone',
        ]

        # GSM config
        self.ctx['connection_name'] = 'gsm-connection'
        # general interface checkings

        # match dict patterns : params to be applied (str: str)
        self.interface_config = [
            [
                {
                    'connection_name': "{{ connection_name }}",
                    'type': 'gsm',
                },
                {
                    'ipv4.route-metric': '101',
                },
            ],
        ]

    def get_state(self):
        self.find_modem()  #  force get modem info
        # self.find_cdc()  #  force get modem info

        # get a full-qualified-status (fqs)
        keys = ('state',)  # 'cdc_state'
        state = {k: str(self.ctx.get(k)).lower() for k in keys}

        # analyze fqs

        return state

    @property
    def modem_info(self):
        info = self._modem_info or self.find_modem()
        return info

    @property
    def is_enabled(self):
        _info = self.modem_info
        state = self.ctx.get('state')
        if not state or re.search(r"(?imsx)disabled|off", state):
            return False

        return True

    @property
    def is_configured(self):
        _info = self.modem_info
        state = self.ctx.get('state')
        if not state or re.search(r"(?imsx)disabled|registered", state):
            return False

        return True

    def find_modem(self):
        result = self.collect(self.FIND_MODEM)
        if result:
            result = self.collect(self.GET_MODEM_INFO)
            if result:
                self._modem_info = result
                return result
        else:
            # no modem found!
            self.forget_modem()

    def forget_modem(self):
        self.ctx.pop('modem_id', None)
        self.ctx.pop('state', None)
        self.ctx.pop('cdc_state', None)

    def find_cdc(self):
        result = self.collect(self.get_command(self.FIND_CDC))
        return result

    def _populate_patterns(self):
        # -------------------------------------------------
        # FIND_MODEM
        # -------------------------------------------------
        self.add(
            self.FIND_MODEM,
            'mmcli -L',
            [
                (
                    'modem_info',
                    """(?imsux)
                    /org/freedesktop/ModemManager\d+/Modem/(?P<modem_id>\d+)
                    """,
                ),
            ],
            False,
        )

        # -------------------------------------------------
        # GET_MODEM_INFO
        # -------------------------------------------------

        # General
        self.add(
            self.GET_MODEM_INFO,
            'mmcli --modem={{ modem_id }}',
            [
                (
                    'general',
                    """(?imsux)
                    General.*?
                    device\s+id:\s+(?P<device_id>[a-f0-9]+)
                    """,
                ),
                (
                    'hardware',
                    """(?msx)
                    Hardware
                    .*?manufacturer:\s+(?P<manufacturer>[^\n]+)
                    .*?model:\s+(?P<model>[^\n]+)
                    .*?equipment\s+id:\s+(?P<equipment_id>[^\n]+)
                    """,
                ),
                (
                    'system',
                    """(?msx)
                    System
                    .*?device:\s+(?P<device>[^\n]+)
                    .*?drivers:\s+(?P<drivers>[^\n]+)
                    .*?plugin:\s+(?P<plugin>[^\n]+)
                    .*?primary\s+port:\s+(?P<cdc_device>[^\n]+)
                    """,
                ),
                (
                    'status',
                    f"""(?msx)
                    Status
                    .*?\slock:\s+(?P<lock>[^\n]+)
                    .*?\sstate:\s+(\x1b\[\d+m)?(?P<state>[a-z]+)(\x1b\[\d+m)?
                    .*?\spower\s+state:\s+(?P<power_state>[^\n]+)
                    (.*?\ssignal\s+quality:\s+(?P<signal_quality>[^\n]+))?
                    """,
                ),
                (
                    '3g',
                    f"""(?msx)
                    3GPP
                    .*?\simei:\s+(?P<imei>\d+)
                    (.*?\soperator\s+id:\s+(?P<operador_id>[^\n]+))?
                    (.*?\soperator\s+name:\s+(?P<operador_name>[^\n]+))?
                    """,
                ),
                (
                    'sim',
                    f"""(?msx)
                    SIM
                    .*?\sprimary\s+sim\s+path:\s+([^\n]+)SIM/(?P<modem_id>\d+)
                    """,
                ),
                (
                    'sim_slots',
                    f"""(?msx)
                    .*?\s(?P<slot_id>slot\s\d+):\s+(?P<slot_status>[^\n]+)
                    """,
                ),
            ],
            False,
        )
        # -------------------------------------------------
        # GET_NM_CONNECTIONS
        # -------------------------------------------------
        self.add(
            self.GET_NM_CONNECTIONS,
            'nmcli connection show',
            [
                (
                    '__connection_show_header',
                    r"""(?imsx)
                       NAME
                       \s+
                       UUID
                       \s+
                       TYPE
                       \s+
                       DEVICE
                    """,
                ),
                (
                    'connection_show',
                    r"""(?sx)
                       (?P<connection_name>[\w\-]+)
                       \s+
                       (?P<uuid>[a-f0-9\-]+)
                       \s+
                       # TODO: add any other type, but try to avoid [\w\-]+ to match only this response type
                       (?P<type>wifi|tun|bridge|wireguard|gsm)
                       \s+
                       (?P<device>[\w\-]+)
                    """,
                ),
            ],
            False,
        )
        # -------------------------------------------------
        # RENAME_GSM_CONNECTION
        # -------------------------------------------------
        self.add(
            self.RENAME_GSM_CONNECTION,
            "sudo nmcli connection modify uuid {{ uuid }} con-name {{ connection_name }}",
            [],  # no response!
            True,
        )
        # -------------------------------------------------
        # DEL_GSM_CONNECTION_BY_UUID
        # -------------------------------------------------
        self.add(
            self.DEL_GSM_CONNECTION_BY_UUID,
            "sudo nmcli connection delete uuid {{ uuid }}",
            [
                (
                    'nmcli_response',
                    f"""(?imsx)
                    .*?(?P<result>successfully\s+(enabled|connected|added|deleted).*)
                    """,
                )
            ],
            True,
        )
        # -------------------------------------------------
        # GET_NM_CONNECTIONS_PARAM_BY_UUID
        # -------------------------------------------------
        self.add(
            self.GET_NM_CONNECTIONS_PARAM_BY_UUID,
            'nmcli connection show uuid {{ uuid }}',
            [
                (
                    'conn_params',
                    r"""(?msx)
                       \s*
                       (?P<param>[^\s:]+)
                       :\s+
                       (?P<value>.+?)
                       \s*$
                    """,
                ),
            ],
            False,
        )
        # -------------------------------------------------
        # UPDATE_METRIC_GSM_CONNECTION_BY_UUID
        # -------------------------------------------------
        self.add(
            self.UPDATE_METRIC_GSM_CONNECTION_BY_UUID,
            "sudo nmcli connection modify uuid {{ uuid }} {{ param }} {{ value }}",
            [],  #  no response!
            True,
        )
        # -------------------------------------------------
        # UP_GSM_CONNECTION_BY_UUID
        # -------------------------------------------------
        self.add(
            self.UP_GSM_CONNECTION_BY_UUID,
            "sudo nmcli connection up uuid {{ uuid }}",
            [
                (
                    'nmcli_response',
                    f"""(?imsx)
                    .*?
                    Connection\s+
                    (?P<result>successfully\s+(activated|deactivated).*)
                    """,
                )
            ],
            True,
        )
        # -------------------------------------------------
        # ADD_GSM_CONNECTION
        # -------------------------------------------------
        self.add(
            self.MODEM_OPTION,
            "sudo mmcli --modem={{ modem_id }} --{{ option }}",
            [
                (
                    'modem_response',
                    f"""(?imsx)
                    .*?
                    (?P<result>successfully\s+(?P<modem_option>[^\s]+).*)
                    """,
                )
            ],
            True,
        )

        # -------------------------------------------------
        # ADD_GSM_CONNECTION
        # -------------------------------------------------
        self.add(
            self.ADD_GSM_CONNECTION,
            "sudo nmcli connection add type gsm ifname {{ cdc_device }} con-name {{ connection_name }} apn {{ operador_name }}",
            [
                (
                    'connection_response',
                    r"""(?imsx)
                    .*?
                    (?P<result>connection\s+
                       (')?
                       (?P<observed_gsm_connection_name>[^\s']+)
                       (')?
                       \s+
                       (\()?
                       (?P<observed_gsm_uuid>[\w\-]+)
                       (\))?
                       \s+
                       successfully\s+
                       (?P<observed_gsm_connection_status>added|deleted)
                    )
                    """,
                )
            ],
            True,
        )

        # -------------------------------------------------
        # APN_CONNECT
        # -------------------------------------------------
        self.add(
            self.APN_CONNECT,
            "sudo mmcli --modem={{ modem_id }} --simple-connect=apn={{ apn_name }},ip-type=ipv4v6",
            [
                (
                    'nmcli_response',
                    f"""(?imsx)
                    .*?(?P<result>successfully\s+(enabled|connected|added|deleted).*)
                    """,
                )
            ],
            True,
        )

    def _foo_pending(self):
        self.commands[self.FIND_CDC] = 'nmcli'
        self.commands[
            self.GET_CDC_WDM_INTERFACE
        ] = 'nmcli'  # TODO: neccesary ?

        self.commands[self.GET_CDC_WDM_INTERFACE] = "nmcli"

        self.commands[
            self.DEL_GSM_CONNECTION_BY_NAME
        ] = "sudo nmcli connection delete {connection_name}"

        self.commands[
            self.UP_GSM_CONNECTION_BY_NAME
        ] = "sudo nmcli connection up {connection_name}"

        # NetworkManager
        ## cdc-wdm0: disconnected

        self.add(
            2500,
            'cdc_device',
            f"""(?msx)
            .*?(?P<cdc_device>cdc-wdm\d+)
            :\s+(\x1b\[\d+m)?(?P<cdc_state>[a-z]+)(\x1b\[\d+m)?
            """,
        )

        txt = """
        NAME            UUID                                  TYPE  DEVICE
        gsm-connection  b67d42c1-4a25-449e-a54c-96a24bfbca72  gsm   cdc-wdm0
        gsm-connection  ba82f33b-b5e5-4348-9c1b-dcfd22247604  gsm   --
        """

        txt = """
        connection.id:     gsm-connection
        connection.uuid:   05447a24-5968-4582-a344-4855c1605008

        """

        m = re.search(
            r"""(?msx)
               \s*
               (?P<param>[^\s:]+)
               :\s+
               (?P<value>.+?)
               \s*$
               (?P<tail>.*)
            """,
            txt,
        )
        if m:
            d = m.groupdict()
            for k, v in d.items():
                print(f"{k}: {v}")
            # print(d)
            foo = 1

        foo = 1

    # STM handlers
    async def do_state_none(self, **kw):
        self.echo("WARNING: No GSM modem found!!!")
        self.slowdown()

    async def do_state_disabled(self, option='enable', **kw):
        # mmcli --modem=0 --enable
        result = self.collect(self.MODEM_OPTION, option=option)
        # self.echo(str(result))

    async def do_state_registered(self, **kw):
        """
        sudo mmcli -m 0 --simple-connect='apn=Movistar,ip-type=ipv4v6'
        successfully connected the modem
        """
        assert (
            not self.is_configured
        ), "TODO: check if is possible a 'hot-reconfiguration'"

        for apn in self.ctx['APN']:  # must exists
            self.ctx['apn_name'] = apn  # TODO: can use just 'operador_name'?
            result = self.collect(self.APN_CONNECT)
            # print(f"result: {result}")
            if re.search(r"successfully", str(result)):
                print(f"Ok, connected to the Network")
                break

    def _hide_do_state_connected_cdc_state_disconnected(self, **kw):
        """
        Modem is connected to GSM network, but GSM interface
        is not configured
        """
        self.echo("create missing GSM inferface for {cdc_device}")

        cmd = self.get_command(self.GET_NM_CONNECTIONS)
        result = self.collect(cmd)
        print(result)
        if not result:
            result = self.collect(self.ADD_GSM_CONNECTION)

            ## just delete fo testing
            # cmd = self.get_command(self.DEL_GSM_CONNECTION)
            # result = self.collect(cmd)

    def _add_gsm_connection(self):
        self.echo(
            "Add GSM interface connection: {connection_name} using apn: {operador_name}"
        )
        result = self.collect(self.ADD_GSM_CONNECTION)
        self.echo("result --> {result}")

        # review
        result = self.collect(self.UP_GSM_CONNECTION_BY_NAME)
        foo = 1

    def _hide_activate_interface(self, **kw):
        # self.echo(
        # "Priorize '{connection_name}' connection changing metrics"
        # )
        # cmd = self.get_command(self.UPDATE_METRIC_GSM_CONNECTION_BY_UUID)
        # result = self.collect(cmd)

        # self.echo("Reactivate connection so changes will become active")
        # cmd = self.get_command(self.UP_GSM_CONNECTION_BY_UUID, **kw)
        # result = self.collect(cmd)
        result = self.collect(self.UP_GSM_CONNECTION_BY_UUID, **kw)
        foo = 1

    async def do_state_connected(self, **kw):
        """
        Delete Any duplicated connection
        -------------------------------------------------

        nmcli connection show
        stdout:
        NAME            UUID                                  TYPE  DEVICE
        gsm-connection  b67d42c1-4a25-449e-a54c-96a24bfbca72  gsm   cdc-wdm0
        gsm-connection  ba82f33b-b5e5-4348-9c1b-dcfd22247604  gsm   --

        Check Metric
        -------------------------------------------------

        user@venoen241:~$ route -n
        Kernel IP routing table
        Destination     Gateway         Genmask         Flags Metric Ref    Use Iface
        0.0.0.0         192.168.5.1     0.0.0.0         UG    100    0        0 enp1s0
        0.0.0.0         10.82.227.120   0.0.0.0         UG    700    0        0 wwx2a3bdd806a72
        10.25.128.1     192.168.5.1     255.255.255.255 UGH   100    0        0 enp1s0
        10.82.227.112   0.0.0.0         255.255.255.240 U     700    0        0 wwx2a3bdd806a72
        10.220.0.0      0.0.0.0         255.255.0.0     U     0      0        0 wg0
        80.58.61.250    192.168.5.1     255.255.255.255 UGH   100    0        0 enp1s0
        80.58.61.254    192.168.5.1     255.255.255.255 UGH   100    0        0 enp1s0
        192.168.0.0     0.0.0.0         255.255.0.0     U     100    0        0 enp1s0
        192.168.5.1     0.0.0.0         255.255.255.255 UH    100    0        0 enp1s0

        nmcli connection modify  {{ connection_name }} ipv4.route-metric 0

        user@venoen241:~$ route -n
        Kernel IP routing table
        Destination     Gateway         Genmask         Flags Metric Ref    Use Iface
        0.0.0.0         10.82.227.120   0.0.0.0         UG    0      0        0 wwx2a3bdd806a72
        0.0.0.0         192.168.5.1     0.0.0.0         UG    100    0        0 enp1s0
        10.25.128.1     192.168.5.1     255.255.255.255 UGH   100    0        0 enp1s0
        10.82.227.112   0.0.0.0         255.255.255.240 U     0      0        0 wwx2a3bdd806a72
        10.220.0.0      0.0.0.0         255.255.0.0     U     0      0        0 wg0
        80.58.61.250    192.168.5.1     255.255.255.255 UGH   100    0        0 enp1s0
        80.58.61.254    192.168.5.1     255.255.255.255 UGH   100    0        0 enp1s0
        192.168.0.0     0.0.0.0         255.255.0.0     U     100    0        0 enp1s0
        192.168.5.1     0.0.0.0         255.255.255.255 UH    100    0        0 enp1s0

        sudo nmcli connection up {{ connection_name }}

        """

        # check connections managed by NetworkManager
        result = self.collect(self.GET_NM_CONNECTIONS)
        connections = result.get('connection_show', {})
        if isinstance(connections, dict):
            connections = [connections]

        def expected_connection():
            nonlocal connections  # preserve external object id
            # check expected gsm connection
            # if there is any already configured and active but
            # its name is different, then we will rename the connection
            for conn in connections:
                assert isinstance(conn, dict)
                if len(conn) < 1:
                    continue
                print(f"checking: {conn}")
                if (
                    conn.get('type') in ('gsm',)
                    and conn.get('device') == self.ctx['cdc_device']
                ):
                    if (
                        conn['connection_name']
                        != self.ctx['connection_name']
                    ):
                        # rename connection
                        # self.ctx['connection_renamed_uuid'] = conn['uuid']
                        self.echo(
                            f"Renaming connection: name: {conn['connection_name']} uuid={conn['uuid']} --> {self.ctx['connection_name']}"
                        )

                        result = self.collect(
                            self.RENAME_GSM_CONNECTION, uuid=conn['uuid']
                        )
                        # reload connections in this case
                        result = self.collect(self.GET_NM_CONNECTIONS)
                        connections = result.get('connection_show', {})

                        foo = 1
                    break
            else:
                # is missing
                result = self.collect(self.ADD_GSM_CONNECTION)
                result = self.collect(self.GET_NM_CONNECTIONS)
                connections = result.get('connection_show', {})

                # agp: not neccessary. It will be done next cycle
                # cmd = self.get_command(self.GET_NM_CONNECTIONS)
                # result = self.collect(cmd)
                # connections = result.get('connection_show', {})

        def clean_connections():
            nonlocal connections
            # check for duplicated GSM connections managed by this agent
            # check for duplicated connections, just gsm ones
            for conn in connections:
                assert isinstance(conn, dict)
                if len(conn) < 1:
                    continue
                if conn.get('type') in ('gsm',) and (
                    (
                        conn.get('connection_name')
                        == self.ctx['connection_name']
                        and conn.get('device') != self.ctx['cdc_device']
                    )
                    or (
                        conn.get('connection_name')
                        != self.ctx['connection_name']
                        # and conn['device'] == self.ctx['cdc_device']
                    )
                ):
                    # self.ctx['connection_deleted_uuid'] = conn['uuid']
                    self.echo(
                        f"Deleting connection: name: {conn['connection_name']} uuid={conn['uuid']}"
                    )

                    result = self.collect(
                        self.DEL_GSM_CONNECTION_BY_UUID, **conn
                    )
                    foo = 1

        def check_connecion_params():
            nonlocal connections

            for conn in connections:
                assert isinstance(conn, dict)
                if len(conn) < 1:
                    continue
                template = self.reactor.env.from_string

                for patterns, params in self.interface_config:
                    m = [
                        # conn.get(k) == v.format_map(self.ctx)
                        conn.get(k) == template(v).render(self.ctx)
                        for k, v in patterns.items()
                    ]
                    if all(m):
                        # match
                        self.echo(f"ok, interface match: {conn}")
                        result = self.collect(
                            self.GET_NM_CONNECTIONS_PARAM_BY_UUID,
                            split_lines=True,
                            **conn,
                        )
                        info = {}
                        for d in result['conn_params']:
                            info[d['param']] = d['value']

                        modified = False
                        for param, value in params.items():
                            if value != info[param]:
                                self.echo(
                                    "changing param: {param}:  {old} ---> {new}",
                                    param=param,
                                    old=info[param],
                                    new=value,
                                )
                                result = self.collect(
                                    self.UPDATE_METRIC_GSM_CONNECTION_BY_UUID,
                                    param=param,
                                    value=value,
                                    **conn,
                                )
                                modified = True
                                foo = 1

                        if modified:
                            result = self.collect(
                                self.UP_GSM_CONNECTION_BY_UUID, **conn
                            )
                        foo = 1

                pass

        expected_connection()
        clean_connections()
        check_connecion_params()

        # self._activate_gsm_metrics()

        self.slowdown()
        foo = 1


class MQTTWatcher(Agent):
    """A system WatchDog"""

    PING = 'ping'
    REBOOT = 'reboot'

    def __init__(self, name='mqtt-watcher', *args, **kw):
        super().__init__(name=name, *args, **kw)

        self.ctx['sleep'] = 5
        self.ctx['max_failures'] = 5
        # rotating hosts in failure case
        self.ctx['hosts'] = [
            '8.8.8.8',  # google.com
            '8.8.4.4',  # google.com
            'akamai.com',
            'microsoft.com',
        ]

        self.client = aiomqtt.Client(
            hostname="test.mosquitto.org",  # The only non-optional parameter
        )

    async def _boot_listen(self):
        for i in range(10):
            print(f"- booting  {i} !!")
            await sleep(0.1)
        print(f"- Boot OK !!")
        foo = 1

    async def _fiber_listen(self):
        t0 = t1 = time.time()
        try:
            async with aiomqtt.Client(
                "test.mosquitto.org", keepalive=120
            ) as self.client:
                async with self.client.messages() as messages:
                    await self.client.subscribe("#")
                    async for message in messages:
                        received = self.inc_counter('i_received')

                        #  message.topic.matches('temperature')
                        if re.match(
                            r'.*(value|temperature).*', message.topic.value
                        ):
                            processed = self.inc_counter('i_processed')
                            t2 = time.time()
                            elapsed = t2 - t1
                            if elapsed > 10 or not processed % 1000:
                                rec_speed = int(received / (t2 - t0))
                                prc_speed = int(processed / (t2 - t0))

                                print(
                                    f"[rec: {received}, {rec_speed}/sec] [proc: {processed}, {prc_speed}/sec], message.topic: {message.topic}"
                                )
                                foo = 1
                            t1 = t2

        except Exception as why:
            print(why)
            self.running = False

            # if message.topic.matches("humidity/outside"):
            # print(f"[humidity/outside] {message.payload}")
            # if message.topic.matches("+/inside"):
            # print(f"[+/inside] {message.payload}")
            # if message.topic.matches("temperature/#"):
            # print(f"[temperature/#] {message.payload}")

    def _populate_patterns(self):
        # -------------------------------------------------
        # FIND_MODEM
        # -------------------------------------------------
        # Ok case
        # PING 8.8.8.8 (8.8.8.8) 56(84) bytes of data.
        # 64 bytes from 8.8.8.8: icmp_seq=1 ttl=116 time=8.66 ms
        #
        # --- 8.8.8.8 ping statistics ---
        # 1 packets transmitted, 1 received, 0% packet loss, time 0ms
        # rtt min/avg/max/mdev = 8.659/8.659/8.659/0.000 ms

        # Wrong case
        # ping -c 1  -W 5 8
        # PING 8 (0.0.0.8) 56(84) bytes of data.

        # --- 8 ping statistics ---
        # 1 packets transmitted, 0 received, 100% packet loss, time 0ms

        self.add(
            self.PING,
            'ping -c 1 -W 3 {{ host }}',
            [
                (
                    'ping_info',
                    r"""(?imsux)
                    (time=(?P<time>[^\s]+))
                    .*?
                    statistics
                    .*?
                    (?P<received>\d+)\s*received
                    """,
                ),
                (
                    'ping_info',
                    r"""(?imsux)
                    statistics
                    .*?
                    (?P<received>\d+)\s*received
                    """,
                ),
            ],
            False,
        )
        self.add(
            self.REBOOT,
            "sudo shutdown -r now 'Reboot due internet connection malfunction'",
            [
                (
                    'reboot_info',
                    r"""(?imsux)
                    (?P<response>.*)
                    """,
                ),
            ],
            True,
        )

        text = """PING 8 (0.0.0.8) 56(84) bytes of data.

        # --- 8 ping statistics ---
        # 1 packets transmitted, 0 received, 100% packet loss, time 0ms
"""
        pattern = r"""(?imsux)
                    statistics
                    .*?
                    (?P<received>\d+)\s*received
                    """
        # m = re.search(pattern, text)
        # d = m.groupdict()
        # print(d)
        # foo = 1

    async def do_state_idle(self, **kw):
        """
        ok   response: {'ping_info': {'time': None, 'received': '1'}}
        fail response: {'ping_info': {'time': None, 'received': '0'}}
        """
        self.echo(f"{self.name} is idle !!")
        hosts = self.ctx['hosts']
        response = self.collect(self.PING, host=hosts[0])
        if self.ctx['received'] in (None, '0'):
            failures = self.inc_counter('reboot')
            self.echo(
                "No ping: count={reboot} < {max_failures}", _expand_=True
            )
            if failures > self.ctx['max_failures']:
                print("REBOOOT NOW!!!!!")
                self.collect(self.REBOOT)
            # rotate hosts in failure case
            hosts.append(hosts.pop(0))
        else:
            failures = self.reset_counter('reboot')

        self.echo(response)
        foo = 1


def test_modem_from_sample():
    mm = Modem()

    text = open('mmcli_modem_unconfigured.txt').read()
    for x in mm.parse(text):
        print(x)

    text = open('mmcli_modem_configured.txt').read()
    for x in mm.parse(text):
        print(x)


def test_modem_already_configured():
    mm = Modem()

    result = mm.find_modem()

    if result:
        print(result)
        assert result['3g']['imei']
        assert result['find_modem']['modem_id']
        assert result['hardware']['equipment_id']

        state = result['status']['state']
        print(f"modem APN: {state}")
        if state in ('connected',):
            modem_id = result['sim']['modem_id']
            assert modem_id
            print(f"modem id: {modem_id}")

            assert result['system']['cdc_device']
            assert result['sim_slots'][0]['slot_status']

        else:
            pass
        print(f"Ok")

    mm.configure()

    # for line in sh.run('ls -l', '-l').splitlines():
    # print(line)

    # for x in sh.extract('ls -l'):
    # print(x)
    # foo = 1

    foo = 1


def test_modem_unconfigured():
    mm = Modem()

    result = mm.find_modem()


def test_configure_modem_from_scratch():
    reactor = Reactor()

    modem = Modem()
    reactor.attach(modem)

    run(reactor.main())
    foo = 1


def main():
    reactor = Reactor()

    reactor.attach(Modem())
    reactor.attach(WatchDog())
    # reactor.attach(MQTTWatcher())

    run(reactor.main())
    foo = 1


if __name__ == '__main__':
    # test_files()
    # test_modem_from_sample()
    # test_modem_already_configured()
    # test_modem_unconfigured()
    # test_configure_modem_from_scratch()
    main()
