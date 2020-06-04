import discord
from discord.ext import commands, tasks
import asyncio
from datetime import datetime
import os
import yaml
from logger import logger


with open('configs/token.yml', 'r') as f:
    token = yaml.safe_load(f)['Token']
client = commands.Bot(command_prefix='.')


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

client.run(token)
