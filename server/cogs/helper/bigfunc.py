'''
pattern

content=None, *, tts=False, embed=None, file=None,
files=None, delete_after=None, nonce=None

'''


def echo(string):
    return {'content': string}


def bigfunc(func, params):
    return globals()[func](params)


if __name__ == '__main__':
    pass
