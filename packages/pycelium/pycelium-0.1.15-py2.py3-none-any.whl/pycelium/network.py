from .definitions import DNS_FACTS, PING_FACTS
from .gathering import GatherFact


class PingFact(GatherFact):
    def __init__(self, merge=True, prefix=PING_FACTS, *args, **kw):
        super().__init__(merge=merge, sudo=False, prefix=prefix, *args, **kw)
        self.cmdline = "ping -c 1 -W 3 {{ name }}"

    def _populate_interactions(self):
        """
        Server:		127.0.0.53
        Address:	127.0.0.53#53

        Name:	sentinel
        Address: 195.57.78.183

        or

        Server:		127.0.0.53
        Address:	127.0.0.53#53

        ** server can't find sentinela: SERVFAIL

        """
        super()._populate_interactions()
        self.add_interaction(
            '200_get-ping',
            r"""(?imsux)
            PING\s(?P<key>[^\s]+).*
            .*?\s
            (?P<received>\d+)\s*received,\s+0%\spacket\sloss.*
            """,
            'set_object_tm',
        )
        self.add_interaction(
            '400-ping-error',
            r"""(?imsux)
            PING\s(?P<key>[^\s]+).*
            .*?\s
            (?P<received>0)\s*received,\s+100%\spacket\sloss.*
            """,
            'set_object_tm',
        )
        self.add_interaction(
            '400_ping-dns',
            r"""(?imsux)
            ping:\s(?P<key>[^\s:]+).*service\s+not\s+known
            """,
            'set_dns_error',
        )


class NSLookup(GatherFact):
    """
    TBD
    """

    def __init__(self, merge=True, prefix=DNS_FACTS, *args, **kw):
        super().__init__(merge=merge, prefix=prefix, *args, **kw)
        self.cmdline = "nslookup {{ name }}"

    def _populate_interactions(self):
        """
        Server:		127.0.0.53
        Address:	127.0.0.53#53

        Name:	sentinel
        Address: 195.57.78.183

        or

        Server:		127.0.0.53
        Address:	127.0.0.53#53

        ** server can't find sentinela: SERVFAIL

        """
        super()._populate_interactions()
        self.add_interaction(
            '200_get_hostip',
            r'Name:\s+(?P<key>[^\s]+)\s+Address:\s+(?P<value>[\d\.]+)',
            'set_attribute',
        )
        self.add_interaction(
            '400_lookup-fail',
            r'.*server\s+can.*find.*SERVFAIL',
        )
