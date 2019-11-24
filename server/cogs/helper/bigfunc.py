from .reddit import top_day_sub as rtop, random_image_sub as rdom
import logging

'''
pattern

content=None, *, tts=False, embed=None, file=None,
files=None, delete_after=None, nonce=None

'''

logger = logging.getLogger('rpi4.bigfunc')


def echo(string):
    return {'content': string}


def bigfunc(func, params):
    logging.info(f'bigfunc {func}')
    return globals()[func](params)


if __name__ == '__main__':
    print(globals().keys())
