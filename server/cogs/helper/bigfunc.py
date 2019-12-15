from .reddit import top_day_sub as rtop, random_image_sub as rdom
from .reddit import discord_harvester as dscd
from .reddit import user_track as ustk
import logging

'''
pattern

content=None, *, tts=False, embed=None, file=None,
files=None, delete_after=None, nonce=None

'''

logger = logging.getLogger('rpi4.bigfunc')


async def echo(string):
    return {'content': string}


async def bigfunc(func, params):
    logging.info(f'bigfunc {func}')
    return await globals()[func](params)


if __name__ == '__main__':
    print(globals().keys())
