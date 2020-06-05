import discord
import os
from discord.ext import commands
import logging


logger = logging.getLogger('rpi4.basic')
#  creator_id = int(os.getenv('CREATOR_ID'))


class Basic(commands.Cog):

    def __init__(self, client):
        self.client = client
    #  events

    #  commands
    @commands.command()
    async def ping(self, ctx):
        logger.debug('ping command')
        await ctx.send(f'ping_rpi: {round(self.client.latency * 1000)}ms')
        
    @commands.command()
    async def plic(self, ctx):
        logger.debug('placeholder pic command')
        file = discord.File('temp/plic.jpg', filename='plic.jpg', spoiler=False)
        embed = discord.Embed()
        embed.set_image(url="attachment://plic.jpg")
        await ctx.send(file=file, embed=embed)  


def setup(client):
    client.add_cog(Basic(client))
