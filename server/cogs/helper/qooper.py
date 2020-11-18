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
        self.q = qconnection.QConnection(host='localhost', port=port)
        self.idloc = idloc
        self.idx = {}
    
    async def save_ids(self, message):
        await self.update_idx(message.author.id, message.author.name)
        # print(message.created_at)
        await self.update_idx(message.guild.id, message.guild.name)
        await self.update_idx(message.channel.id, message.channel.name)

    async def update_idx(self, key, value):
        if key not in self.idx:
            self.idx[key] = value
            await self.save_idx()

    @asyncify
    def save_idx(self):
        with open(self.idloc, 'w') as f:
            json.dump(self.idx, f)

    @asyncify
    def load_idx(self):
        try:
            with open(self.idloc, 'r') as f:
                self.idx = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            pass


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    x = DiscordFeeder('data/idx.json', 42069)
    loop.run_until_complete(x.load_idx())
