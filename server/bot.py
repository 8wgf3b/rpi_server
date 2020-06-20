import discord
from discord.ext import commands, tasks
import asyncio
from cogs.helper.bigfunc import bigfunc
from cogs.helper.db import fetch_update_to_be_run
from datetime import datetime
import os
from logger import logger


token = os.getenv('DISCORD_TOKEN')
client = commands.Bot(command_prefix='.')


@client.event
async def on_ready():
    logger.info('Bot is online')
    cron_tasks.start()


@tasks.loop(minutes=30)
async def cron_tasks():
    await client.wait_until_ready()
    logger.info('Starting cron looper')
    base = datetime.utcnow()
    to_do = fetch_update_to_be_run(base)
    logger.debug('fetched tasks to be run')
    for result in to_do:
        try:
            message = await bigfunc(result.func, result.params)
            cid = int(result.channel_id)
            channel = client.get_channel(cid)
            await channel.send(**message, delete_after=21600)
            logger.debug(f'successful task#{result.id}')
        except TypeError:
            logger.info('Empty message')
        except Exception as e:
            logger.exception(f'Unable to send a message for task#{result.id}')
    logger.info('Finished cron looper')


@client.command()
async def load(ctx, extension):
    logger.info(f'Loading {extension} for {ctx.guild} {ctx.channel.name}')
    client.load_extension(f'cogs.{extension}')


@client.command()
async def unload(ctx, extension):
    logger.info(f'Unloading {extension} for {ctx.guild} {ctx.channel.name}')
    client.unload_extension(f'cogs.{extension}')


@client.command()
async def reload(ctx, extension):
    logger.info(f'reloading {extension} for {ctx.guild} {ctx.channel.name}')
    client.unload_extension(f'cogs.{extension}')
    client.load_extension(f'cogs.{extension}')


for filename in os.listdir('./cogs'):
    if not filename == '__init__.py' and filename.endswith('.py'):
        logger.info(f'Loading cog {filename}')
        client.load_extension(f'cogs.{filename[:-3]}')

client.run(token)
