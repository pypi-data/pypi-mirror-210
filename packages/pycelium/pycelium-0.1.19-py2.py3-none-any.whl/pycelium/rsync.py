from .tools import parse_uri, expandpath

from .shell import DefaultExecutor
from .action import Action


class Rsync(Action):
    """ """

    def __init__(self, source, target, *args, **kw):
        self._stop_no_seq = False  # wait until fibers have done
        super().__init__(*args, **kw)
        self.source = source
        self.target = target
        foo = 1

    # --------------------------------------------------
    # Coded as sequence: # TODO: review
    # --------------------------------------------------
    async def _seq_10_rsync_local(self, *args, **kw):
        cwd = expandpath('.')
        self.local = DefaultExecutor(host='localhost', cwd=cwd)
        self.reactor.attach(self.local)

        return True

    async def _seq_20_rsync_exec(self, *args, **kw):
        _uri = parse_uri(self.target)
        _uri['path'] = self.target.split(':')[-1]

        cmdline = 'rsync -az {{source }} {{ xhost }}:{{ path }}'
        cmd = self.expand(cmdline, **_uri)
        result = await self.local.exec_many(cmd, sudo=False)
        self.local._term()
        return result
