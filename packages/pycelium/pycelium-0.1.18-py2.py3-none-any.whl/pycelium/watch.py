from .definitions import REBOOT_FACTS
from .agent import Agent
from .network import PingFact


from .gathering import GatherFact


class Reboot(GatherFact):
    def __init__(
        self, force=False, merge=True, prefix=REBOOT_FACTS, *args, **kw
    ):
        super().__init__(merge=merge, sudo=True, prefix=prefix, *args, **kw)
        self.force = force
        # self.cmdline = "echo 'reboot'"
        self.cmdline = "reboot"

    async def _enter_boot(self, *args, **kw):
        executor = await self.is_connected()
        if executor:
            host = executor.ctx.get('host', 'unkown_host')
            local_hostname = executor.ctx.get(
                'local_hostname', 'unkown_localhost'
            )

            # TODO: remove
            if local_hostname in ('dev00') and host in (
                'dev00',
                'localhost',
            ):
                self.log.warning(
                    f"skip rebooting '{local_hostname}' host. Just remove this in production!!"
                )
                self.push(self.EV_KILL)
                return

            self.log.warning(f"Rebooting '{host}' machine")
            await super()._enter_boot(*args, **kw)
        else:
            self.log.warning(f"No executor found...???. Skipping reboot")


class WatchDog(Agent):
    """A system WatchDog"""

    PING = 'ping'
    REBOOT = 'reboot'
    EV_REBOOT = 'Reboot'

    def __init__(self, name='watchdog', *args, **kw):
        super().__init__(name=name, *args, **kw)

        self.ctx['sleep'] = 60
        self.ctx['max_failures'] = 5
        # rotating hosts in failure case
        self.ctx['hosts'] = [
            '8.8.8.8',  # google.com
            '8.8.4.4',  # google.com
            'akamai.com',
            'microsoft.com',
        ]
        # self.ctx['hosts'] = [
        #'8.8.8.1',  #  unreacchable
        # ]

    def _build_transitions(self):
        super()._build_transitions()
        s = self
        # --------------------------------------------------
        # STM definition
        # --------------------------------------------------

        s.add_transition(
            s.ST_ANY, s.EV_REBOOT, s.ST_SAME, lambdas=['reboot']
        )

    async def _do_reboot(self):
        self.log.warning(f"rebooting host as requested")
        reboot = self.new_action(Reboot)
        result = await self.wait(reboot)

        foo = 1

    async def _seq_01_test_ping(self, *args, **kw):
        attemps = self.ctx['max_failures']
        while self.running:
            # self.log.warn(f"{self} is alive!!")
            hosts = self.ctx.get('hosts', [])
            if hosts:
                n = len(hosts)
                while n > 0:
                    host = hosts.pop(0)
                    hosts.append(host)
                    ping = self.new_action(PingFact, name=host)
                    result = await self.wait(ping)
                    if not any(result):
                        attemps = self.ctx['max_failures']
                        break
                    n -= 1
                if n <= 0:
                    attemps -= 1
                    if attemps > 0:
                        self.log.warning(
                            f"no ping received after trying ({len(hosts)}) hosts: remaining attemps: {attemps}"
                        )
                    else:
                        self.log.error(
                            f"It's seems Network is down, request a host reboot"
                        )
                        self.push(self.EV_REBOOT)

            else:
                self.log.error(f"No hosts are defined for ping")

            await self.sleep(self.ctx['sleep'])
            foo = 1
