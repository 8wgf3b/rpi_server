import discord
from discord.ext import commands, tasks
import asyncio
from datetime import datetime
import os
import yaml
from logger import logger
import zmq
import zmq.asyncio


with open('configs/token.yml', 'r') as f:
    auth_dic = yaml.safe_load(f)
client = commands.Bot(command_prefix='!')


ctx = zmq.asyncio.Context()
socket = ctx.socket(zmq.REP)
socket.bind("tcp://*:5555")


@client.event
async def on_ready():
    logger.info('Bot is online')


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


async def receiver():
    while True:
        message = await socket.recv_pyobj()
        channel = client.get_channel(int(auth_dic['PushChannel']))
        try:
            await channel.send(**message)
        except Exception as e:
            await channel.send(f'{repr(e)}:\n\n{repr(message)}')
        await asyncio.sleep(1)
        await socket.send_pyobj("received")

client.loop.create_task(receiver())
client.run(auth_dic['Token'])
