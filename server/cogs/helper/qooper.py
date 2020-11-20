import json
from qpython import qconnection
from qpython.qcollection import qlist, QDictionary
from qpython.qtype import QException
import numpy as np
try:
    from .utils import asyncify
except ModuleNotFoundError:
    from utils import asyncify
    import asyncio


class DiscordFeeder:
    def __init__(self, idloc, port):
        try:
            self.q = qconnection.QConnection(host='localhost', port=port)
            self.q.open()
        except ConnectionRefusedError:
            print('oops')
        self.idloc = idloc
        self.load_idx()
    
    def save_ids(self, message):
        self.update_idx(message.author.id, message.author.name)
        self.update_idx(message.guild.id, message.guild.name)
        self.update_idx(message.channel.id, message.channel.name)
        dt = message.created_at
        time = (np.datetime64(dt) - np.datetime64(dt, 'D')).astype('timedelta64[ms]')
        dt = np.datetime64(dt, 'D')
        print(dt, time)

    def update_idx(self, key, value):
        if key not in self.idx:
            self.idx[key] = value
            self.save_idx()

    # @asyncify
    def save_idx(self):
        with open(self.idloc, 'w') as f:
            json.dump(self.idx, f)

    # @asyncify
    def load_idx(self):
        try:
            with open(self.idloc, 'r') as f:
                self.idx = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.idx = {}

    def save_message(self, message):
        self.save_ids(message)
        try:
            pass
        except QException:
            pass


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    x = DiscordFeeder('data/idx.json', 42069)
    loop.run_until_complete(x.load_idx())
