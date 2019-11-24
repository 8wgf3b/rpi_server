import discord
import os
from discord.ext import commands
from .helper.db import create_new_task, clear_channel_tasks
from .helper.db import pretty_channel_tasks, delete_by_ids
import logging


logger = logging.getLogger('rpi4.basic')
creator_id = int(os.getenv('CREATOR_ID'))


class Basic(commands.Cog):

    def __init__(self, client):
        self.client = client
    #  events

    #  commands
    @commands.command()
    async def ping(self, ctx):
        logger.debug('ping command')
        await ctx.send(f'ping: {round(self.client.latency * 1000)}ms')

    @commands.command()
    @commands.check(lambda x: x.author.id == creator_id)
    async def sched(self, ctx, *, text):
        spl = text.split()
        cid = str(ctx.message.channel.id)
        create_new_task(cid, ' '.join(spl[-5:]), spl[0], ' '.join(spl[1:-5]))
        logger.info(f'new task for {cid}')

    @commands.command()
    @commands.check(lambda x: x.author.id == creator_id)
    async def dtbi(self, ctx, *, text):
        spl = text.split()
        cid = str(ctx.message.channel.id)
        spl = [int(x) for x in spl]
        delete_by_ids(spl)
        message = pretty_channel_tasks(cid)
        await ctx.send(message)
        logger.info(f'deleted tasks#{spl}')

    @commands.command()
    @commands.check(lambda x: x.author.id == creator_id)
    async def cct(self, ctx):
        cid = str(ctx.message.channel.id)
        clear_channel_tasks(cid)
        logger.info(f'cleared all {cid} tasks')

    @commands.command()
    @commands.check(lambda x: x.author.id == creator_id)
    async def gct(self, ctx):
        cid = str(ctx.message.channel.id)
        text = pretty_channel_tasks(cid)
        logger.info(f'fetching {cid} tasks')
        await ctx.send(text)

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount=100):
        await ctx.channel.purge(limit=amount)
        logger.info(f'cleared {amount} messages from {cid}')


def setup(client):
    client.add_cog(Basic(client))
