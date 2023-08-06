import sys
import os
import re

from pycelium.tools.containers import simplify

from .definitions import (
    WIREGUARD_FACTS,
    WIREGUARD_ETC,
)
from .shell import (
    temp_filename,
)

# from .action import Action
# from .agent import Agent
from .gathering import GatherFact
from .network import NSLookup


class WireGuard(GatherFact):
    """WG supervisor

    $ sudo wg
    interface: wg-foo
        public key: izCUweAQyhUb6bka8j4xfwchRtjMzOUGBakJI3sxJ1Q=
        private key: (hidden)
        listening port: 3200

    peer: Aee5UO8xbJd7UZegEfOHLsZfdXuQas06bmda6Xy0aVdWWik=
        endpoint: 130.89.148.77:3200
        allowed ips: 10.100.0.0/16
        latest handshake: 45 seconds ago
        transfer: 76.64 KiB received, 81.09 KiB sent
        persistent keepalive: every 20 seconds

    """

    def __init__(
        self, merge=True, prefix=WIREGUARD_FACTS, restart=20, *args, **kw
    ):
        super().__init__(
            merge=merge, prefix=prefix, restart=restart, *args, **kw
        )
        self.cmdline = 'sudo wg show'

    def _populate_interactions(self):
        super()._populate_interactions()
        self.add_interaction(
            '200_get-comment',
            r'\s*#[^\n$]*',
        )
        self.add_interaction(
            '200_get-interface-group',
            r'interface:\s*(?P<key>.*?)(\n|$)',
            'new_group',
        )

        self.add_interaction(
            '200_get-peer-group',
            r'peer:\s*(?P<key>[^:\n]+)\s*(\n|$)',
            'new_nested_group',
            prefix='peer',
        )
        self.add_interaction(
            '250_get-parameter',
            '(?P<key>[^\s][^:]+):\s*(?P<value>[^\n$]+)(\n|$)',
            'set_attribute',
            preserve_value=True,
        )
        self.add_interaction(
            '240_get-parameter',
            '(?P<key>persistent\s+kee[^:]+):\s*every\s*(?P<value>\d+)\s*.*?(\n|$)',
            'set_attribute',
            preserve_value=True,
        )

    async def _fiber_ipchaning(self, *args, **kw):
        """
        Note: Run locally as well, not only remotely

        """
        relativebp = {f'.*.endpoint': '.*'}

        while self.running:
            await self.sleep(5)

            # action = self.new_action(NSLookup, name='wg.server.com')
            # result = await self.wait(action)

            # spec = '.'.join(self.prefix)
            # blueprint = {f'.*{spec}.*.endpoint': '.*'}
            # result = self.search(blueprint, flat=False)
            # result = deindent_by(result, self.prefix)
            # await self.sleep(5.51)

            result = self.lens(relativebp)

            temp = temp_filename()

            for interface, live in result.items():
                path = f'/etc/wireguard/{interface}.conf'
                if not await self.default_executor.get(path, temp):
                    self.log.error(f"Unable to get file: {path} ...")
                    continue

                prefix = WIREGUARD_ETC + (interface,)

                config = self.new_action(
                    WireguardParseConfig,
                    prefix=prefix,
                    name=temp,
                    interface=interface,
                )
                await self.wait(config)

                # spec = '.'.join(config.prefix)
                # blueprint = {f'.*{spec}.*.endpoint': '.*'}
                # etc = config.search(blueprint, flat=False)
                # etc = deindent_by(etc, etc.prefix)
                etc = config.lens(relativebp)

                etc = etc.get('peer', {})
                live = live.get('peer', {})
                for key, live in live.items():
                    live_ep = live.get('endpoint', ':')
                    etc_ep = etc.get(key, {}).get('endpoint', ':')
                    live_host, live_port = live_ep.split(':')
                    etc_host, etc_port = etc_ep.split(':')

                    # check server ip
                    if not re.match(r'[\d\.]+', etc_host):
                        action = self.new_action(NSLookup, name=etc_host)
                        result = await self.wait(action)
                        etc_host = simplify(action.facts).get(etc_host)
                        foo = 1

                    if live_ep == f"{etc_host}:{etc_port}":
                        self.log.debug(
                            f"ok, peer: {key} match endpoints, '{etc_ep}' == '{live_ep}'"
                        )
                        foo = 1
                    else:
                        self.log.warning(
                            f"peer: {key} endpoints doesn't match : '{etc_ep}' == '{live_ep}'"
                        )
                        # set the new peer address
                        action = self.new_action(
                            WireguardSetPeer,
                            interface=interface,
                            peer=key,
                            endpoint=etc_ep,
                        )
                        r = await self.wait(action)
                        if any(r):
                            self.log.error(
                                f"unable to set peer {key} endpoint: {etc_host}"
                            )
                            self.log.error(
                                ''.join([l[0] for l in action.history])
                            )
                        else:
                            self.log.info(
                                f"Ok, endpoint: {etc_ep} is set for peer: {key}"
                            )
                        foo = 1

            await self.sleep(5)
            foo = 1


class WireguardParseConfig(GatherFact):
    """
    # /etc/wireguard/{{ item.basename }}

    # Centesimal VPN

    # ============================================
    # {{ host }} host
    # ============================================
    [Interface]
    PrivateKey = YPsjtJBgsG2SL1EsN2cx9rwktR0aDTqHG/48VYg5jVE=
    # PublicKey = igCUweAQyhUb6bka5j4xfwchRtjMzOUGBakJI3sxJ1Q=
    Address = 10.220.1.243/16
    ListenPort = 3218
    # SaveConfig = true

    # --------------------------------------------
    # Peers
    # --------------------------------------------
    # sentinel server
    [Peer]
    PublicKey = See5UO8xbJd7UZegEsOHLsZdXuQs06bma6Xy0VdWWik=
    AllowedIPs = 10.220.2.33/16
    Endpoint = wg.servre:3218
    PersistentKeepalive = 25
    # PresharedKey = CDtd9kM9ZgF+DSCdooHRw400O/gscH4ScT5bZfv4oDM=
    """

    def __init__(
        self, interface='', merge=True, prefix=WIREGUARD_FACTS, *args, **kw
    ):
        self.interface = interface
        super().__init__(merge=merge, prefix=prefix, *args, **kw)
        try:
            # path = f'/etc/wireguard/{self.interface}.conf'
            self.partial = open(self.name, 'r').read()
        except Exception as why:
            pass
            # self.log.exception(why)
            # self.push(self.EV_KILL)

    def _populate_interactions(self):
        super()._populate_interactions()
        self.add_interaction(
            '200_get-comment',
            r'\s*#[^\n$]*',
        )
        self.add_interaction(
            '200_get-interface-group',
            r"""(?imsx)
            \[Interface\].*
            (?P<key>PrivateKey)\s*=\s*(?P<value>.*?)(\n|$)
            """,
            'set_attribute',
            preserve_value=True,
        )
        self.add_interaction(
            '200_get-peer-group',
            r"""(?imsx)
            \[Peer\].*
            PublicKey\s*=\s*(?P<key>.*?)(\n|$)
            """,
            'new_nested_group',
            prefix='peer',
        )
        self.add_interaction(
            '250_get-parameter',
            '(?P<key>\w+)\s*=\s*(?P<value>[^\s#]+).*(\n|$)',
            'set_attribute',
            preserve_value=True,
        )


class WireguardSetPeer(GatherFact):
    """
    $ sudo wg set wg-project peer See5UO8agea68akl1gsalZdXuQsqfacjlia06bma6Xy0VdWWik= endpoint server.com:3200
    Temporary failure in name resolution: `server.com:3200'. Trying again in 1.00 seconds...
    Temporary failure in name resolution: `server.com:3200'. Trying again in 1.20 seconds...
    Temporary failure in name resolution: `server.com:3200'. Trying again in 1.44 seconds...
    ...
    Temporary failure in name resolution: `server.com:3200'. Trying again in 12.84 seconds...
    Temporary failure in name resolution: `server.com:3200'

    # To add a new peer
    sudo wg set wg-project peer <key> endpoint server.com:3200
    """

    def __init__(
        self,
        interface='',
        peer=None,
        endpoint=None,
        merge=None,
        prefix=WIREGUARD_FACTS,
        *args,
        **kw,
    ):
        self.interface = interface
        self.peer = peer
        self.endpoint = endpoint
        super().__init__(merge=merge, prefix=prefix, *args, **kw)
        self.cmdline = "sudo wg set {{ interface }} peer {{ peer }} endpoint {{ endpoint }}"

    def _populate_interactions(self):
        super()._populate_interactions()
        self.add_interaction(
            '500_error-retry',
            r'Temporary\s+failure.*',
        )
