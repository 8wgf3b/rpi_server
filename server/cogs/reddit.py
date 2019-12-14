import discord
from discord.ext import commands, tasks
import asyncio
from .helper.bigfunc import bigfunc
import logging
import os


logger = logging.getLogger('rpi4.reddit')
creator_id = int(os.getenv('CREATOR_ID'))


class Reddit(commands.Cog):
    def __init__(self, client):
        self.client = client

    #  events
    #  commands


def setup(client):
    client.add_cog(Reddit(client))
