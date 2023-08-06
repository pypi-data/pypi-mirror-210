import re
from functools import reduce

# --------------------------------------
#  sequences
# --------------------------------------


class Sequencer:
    def __init__(self, mutable):
        self.mutable = mutable

        #  prepare

        self.sample = [None] * len(mutable)
        self.keys = []
        self.gen = {}

        # set the fixed part
        for i, (func, exp) in mutable.items():
            if func is None:
                self.sample[i] = exp
            else:
                self.keys.append(i)

        self.pos = 0
        self.total = 1

        if self.keys:
            self.keys.sort(reverse=True)

            # compute all observable ranges
            # to have a progress indicator
            for i in self.keys:
                (func, exp) = mutable[i]
                self.gen[i] = func(exp)
                self.sample[i] = next(self.gen[i])

            self.ranges = {}
            for i in self.keys:
                j = 1
                for _ in self.gen[i]:
                    j += 1
                self.ranges[i] = j

            self.total = reduce(lambda x, y: x * y, self.ranges.values())

    @staticmethod
    def expand_octect(pattern):
        for i in range(0, 256):
            text = str(i)
            if re.match(pattern, text):
                yield text

    @staticmethod
    def expand_range(interval):
        for i in range(*interval):
            text = str(i)
            yield text

    def __iter__(self):
        keys = self.keys
        sample = self.sample
        mutable = self.mutable
        gen = self.gen

        if keys:
            # get fresh sequencers
            for i in keys:
                (func, exp) = mutable[i]
                gen[i] = func(exp)
                sample[i] = next(gen[i])

            while True:
                self.pos += 1
                yield sample
                for i in keys:
                    try:
                        sample[i] = next(gen[i])
                        break
                    except StopIteration:
                        (func, exp) = mutable[i]
                        gen[i] = func(exp)
                        sample[i] = next(gen[i])
                else:  # all generators exhausted
                    return
        else:
            yield sample

    @property
    def progress(self):
        return self.pos / self.total


def expand_network(network):
    """Split network address into pieces and try to expand
    any sub-piece, yielding only addresses that match the
    whole pattern.


    Examples:

    10.220.5-6.*
        10.220.5.0
        10.220.5.1
        ...
        10.220.5.255

    10.220.5-16-2.*
        10.220.5.0
        10.220.5.1
        ...
        10.220.5.255
        10.220.7.0
        10.220.5.1
        ...
        10.220.15.255


    """
    mutable = {}

    # check which patterns canbe expanded or not
    for i, token in enumerate(network.split('.')):
        if re.match(r'\d+$', token):
            # not expandable
            mutable[i] = None, token
        elif token in ('*',):
            mutable[i] = Sequencer.expand_range, (0, 256)
        elif re.match(r'[\d-]+$', token):
            mutable[i] = Sequencer.expand_range, [
                int(x) for x in token.split('-')
            ]
        else:
            # not expandable
            mutable[i] = None, token
            # raise RuntimeError(f"can't handle {token} pattern")

    seq = Sequencer(mutable)
    return seq
    # yield from seq
