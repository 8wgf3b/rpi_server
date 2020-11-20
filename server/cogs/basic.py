import discord
import os
from discord.ext import commands
import logging
from pprint import pprint
from .helper.qooper import DiscordFeeder
import yaml


logger = logging.getLogger('rpi4.basic')
with open('configs/filter.yml', 'r') as f:
    dic = yaml.safe_load(f)
    creator = dic['CREATOR']
    tracked_grp = dic['GROUP']


class Basic(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.qfeed = DiscordFeeder('databases/idx.json', 42069)

    #  events
    @commands.Cog.listener()
    async def on_message(self, message):
        # if message.guild.id == tracked_grp:
        self.qfeed.save_message(message)

    #  commands
    @commands.command()
    async def ping(self, ctx):
        logger.debug('ping command')
        await ctx.send(f'ping_rpi: {round(self.client.latency * 1000)}ms')
 
    @commands.command()
    async def gcid(self, ctx):
        logger.debug('gcid command')
        await ctx.send(ctx.message.channel.id)

    @commands.command()
    async def gaid(self, ctx):
        logger.debug('gcid command')
        await ctx.send(ctx.message.author.id)
        
        
    @commands.command()
    async def plic(self, ctx):
        logger.debug('placeholder pic command')
        file = discord.File('temp/plic.jpg', filename='plic.jpg', spoiler=False)
        embed = discord.Embed()
        embed.set_image(url="attachment://plic.jpg")
        await ctx.send(file=file, embed=embed)  


def setup(client):
    client.add_cog(Basic(client))
