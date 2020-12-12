import websockets
import json
from qpython import qconnection
from qpython.qcollection import qlist, QDictionary
from qpython.qtype import QException
import numpy as np
from datetime import timedelta
import asyncio
try:
    from .utils import asyncify
except ModuleNotFoundError:
    from utils import asyncify


class DiscordFeeder:
    def __init__(self, idloc, tport, cport, rport):
        self.q = qconnection.QConnection(host='localhost', port=tport)
        self.cport = cport
        self.rport = rport
        try:
            self.q.open()
        except ConnectionRefusedError:
            print('oops')
        self.idloc = idloc
        self.load_idx()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.qclient())
        loop.run_until_complete(self.rtsalert())
        loop.run_until_complete(self.cep())
    
    def save_ids(self, message):
        self.update_idx(message.author.id, message.author.name)
        self.update_idx(message.guild.id, message.guild.name)
        self.update_idx(message.channel.id, message.channel.name)

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
        author = np.string_(str(message.author.id))
        channel = np.string_(str(message.channel.id))
        text = bytes(message.content, 'utf-8')
        dt = message.created_at + timedelta(minutes=30, hours=5)
        time = (np.datetime64(dt) - np.datetime64(dt, 'D')).astype('timedelta64[ns]')
        dt = np.datetime64(dt, 'D')
        row = [time, author, dt, channel, text]
        table = np.string_('discord')
        print(row)
        try:
            self.q.sendAsync(".u.upd", table, row, single_char_strings = True) 
        except Exception as e:
            print(e)

    async def rtsalert(self):
        pass

    async def cep(self):
        pass

    async def qclient(self):
        pass


if __name__ == '__main__':
    asyncio.get_event_loop().run_forever()
