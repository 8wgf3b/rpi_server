import discord
from discord.ext import commands, tasks
import asyncio
from cogs.helper.bigfunc import bigfunc
from cogs.helper.db import fetch_update_to_be_run
from datetime import datetime
import os


token = os.getenv('DISCORD_TOKEN')
client = commands.Bot(command_prefix='.')


@client.event
async def on_ready():
    cron_tasks.start()
    print('Bot is online')


@tasks.loop(minutes=2)
async def cron_tasks():
    await client.wait_until_ready()
    base = datetime.utcnow()
    to_do = fetch_update_to_be_run(base)
    for result in to_do:
        try:
            message = bigfunc(result.func, result.params)
            cid = int(result.channel_id)
            channel = client.get_channel(cid)
            await channel.send(**message)
        except Exception as e:
            print(e)
            continue


@client.command()
async def load(ctx, extension):
    client.load_extension(f'cogs.{extension}')


@client.command()
async def unload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')


@client.command()
async def reload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')
    client.load_extension(f'cogs.{extension}')


for filename in os.listdir('./cogs'):
    if not filename == '__init__.py' and filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

client.run(token)
