import praw
import os
from functools import partial
from discord import Embed
from random import choice
import logging
import aiohttp
import re
from .db import fetch_all_bots


logger = logging.getLogger('rpi4.reddit')
reddit = praw.Reddit(client_id=os.environ['CLIENT_ID'],
                     client_secret=os.environ['CLIENT_SECRET'],
                     username=os.environ['USERNAME'],
                     password=os.environ['PASSWORD'],
                     user_agent=os.environ['USER_AGENT'])
logger.debug('Loaded reddit client')


def subreddit_posts(sub='all', time='day', limit=5, type='top'):
    subreddit = reddit.subreddit(sub)
    try:
        if type == 'controversial':
            submissions = subreddit.controversial(time_filter=time, limit=limit)
        elif type == 'hot':
            submissions = subreddit.hot(limit=limit)
        elif type == 'new':
            submissions = subreddit.new(limit=limit)
        elif type == 'random':
            submissions = subreddit.random_rising(limit=limit)
        elif type == 'rising':
            submissions = subreddit.rising(limit=limit)
        elif type == 'top':
            submissions = subreddit.top(time_filter=time, limit=limit)
    except:
        logger.exception('No submissions returned')
        return None
    logger.info(f'fetched {type} posts of {sub}')
    return submissions


async def random_image_sub(params):
    post = next(subreddit_posts(sub=params, limit=1, type='random'))
    embed = Embed(title=params, description=post.title[:200])
    try:
        embed.set_image(url=post.url)
    except:
        logger.exception('failed to create an embed')
    return {'embed': embed}


async def top_day_sub(params):
    split = params.split()
    sub = split[0]
    limit = int(split[1]) if len(split) == 2 else 10
    submisssions = subreddit_posts(sub=sub, type='top', limit=limit)
    description = f'Top {limit} posts for the past 24 hrs'
    embed = Embed(title=sub, description=description)
    for post in submisssions:
        try:
            embed.add_field(name=post.title[:200], value=post.shortlink, inline=False)
        except:
            logger.exception('failed to create an embed')
            continue
    return {'embed': embed}


def find_discord_link(text):
    return re.findall(r'discord.gg/[a-zA-Z0-9\-]*', text)


async def term_searcher(term, after='30m'):
    sub_url = 'https://api.pushshift.io/reddit/submission/search'
    com_url = 'https://api.pushshift.io/reddit/comment/search'
    params = {'q': term,
              'after': after,
              'size': 500}

    async with aiohttp.ClientSession() as session:
        params['fields'] = ','.join(['title', 'selftext', 'subreddit', 'author'])
        async with session.get(sub_url, params=params) as r:
            sub_data = (await r.json())['data']
            logger.info(f'searched submission data for {term}')

    async with aiohttp.ClientSession() as session:
        params['fields'] = ','.join(['body', 'subreddit', 'author'])
        async with session.get(com_url, params=params) as r:
            com_data = (await r.json())['data']
            logger.info(f'searched comments data for {term}')

    return sub_data, com_data


async def discord_harvester(period):
    sub, com = await term_searcher('discord.gg')
    botslist = fetch_all_bots()
    botslist = {x.bot for x in botslist}
    links = dict()
    sub = [x for x in sub if x['author'] not in botslist]
    com = [x for x in com if x['author'] not in botslist]
    for item in sub:
        temp = find_discord_link(item['selftext'])
        temp += find_discord_link(item['title'])
        links = {**links,
                 **{k: item['subreddit'] + ' ' + item['author'] for k in temp}}

    for item in com:
        temp = find_discord_link(item['body'])
        links = {**links,
                 **{k: item['subreddit'] + ' ' + item['author'] for k in temp}}

    message = ''
    for k, v in links.items():
        message += f'{v}\nhttps://{k}\n'

    return {'content': message}


if __name__ == '__main__':
    print(asyncio.run(discord_harvester())['content'])
