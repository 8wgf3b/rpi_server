import discord
import os
from .helper.reddit import make_user_report
from discord.ext import commands
import logging


logger = logging.getLogger('rpi4.reddit')
#  creator_id = int(os.getenv('CREATOR_ID'))


class Reddit(commands.Cog):

    def __init__(self, client):
        self.client = client
    #  events

    #  commands
    @commands.command()
    async def usrp(self, ctx, *, user):
        logger.debug(f'{user} report begin')
        try:
            await make_user_report(user)
            file = discord.File('temp/lol.png', filename=f'{user}.png', spoiler=False)
            embed = discord.Embed(title=f'{user} stats')
            embed.set_image(url=f"attachment://{user}.png")
            await ctx.send(file=file, embed=embed)
            logger.info(f'{user} report sent')
        except Exception as e:
            # Todo: Narrow down the exception
            logger.exception(f'Failed making {user} report')
            await ctx.send('Is the username right bro? Cant make a report :(') 


def setup(client):
    client.add_cog(Reddit(client))
