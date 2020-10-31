import praw
import os
from functools import partial
from discord import Embed
from random import choice
import logging
import aiohttp
import re
import asyncio
from collections import defaultdict
from random import choice
from .util import aiofy

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
    unfil_links = re.findall(r'discord.gg/[a-zA-Z0-9\-]*', text)
    return [f'https://{x}' for x in unfil_links]


async def link_checker(link, lim):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(link) as r:
                invite_page = await r.text()
                members = re.findall(r"with (.+?) other", invite_page)[0]
                members = int(members.replace(',', ''))
                if members <= lim:
                    #  print(link)
                    return True
    except Exception as e:
        print(link)
        logger.exception('Faulty discord link?')
    return False


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


async def discord_harvester(lim='100'):
    lim = int(lim)
    sub, com = await term_searcher('discord.gg')
    links = dict()
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
        if await link_checker(k, lim):
            message += f'{v}\n{k}\n'

    return {'content': message}


async def fetch_user_daily(redditor):
    sub_url = 'https://api.pushshift.io/reddit/submission/search'
    com_url = 'https://api.pushshift.io/reddit/comment/search'
    params = {'author': redditor,
              'after': '30h',
              'size': 500}

    async with aiohttp.ClientSession() as session:
        params['fields'] = ','.join(['title', 'selftext', 'id'])
        async with session.get(sub_url, params=params) as r:
            sub_data = (await r.json())['data']
            logger.info(f'searched submission data for u/{redditor}')

    async with aiohttp.ClientSession() as session:
        params['fields'] = ','.join(['body', 'id', 'link_id'])
        async with session.get(com_url, params=params) as r:
            com_data = (await r.json())['data']
            for comment in com_data:
                comment['link_id'] = comment['link_id'].split('_')[1]
            logger.info(f'searched comments data for u/{redditor}')
    return sub_data, com_data


async def user_track(redditor):
    sub, com = await fetch_user_daily(redditor)
    post_ids = defaultdict(lambda: "")
    for post in sub:
        id, title, body = post['id'], post['title'], post['selftext']
        if len(post_ids[id]) < len(title):
            post_ids[id] = title
        if len(post_ids[id]) < len(body):
            post_ids[id] = body

    for comment in com:
        id, body = comment['link_id'], comment['body']
        if len(post_ids[id]) < len(body):
            post_ids[id] = body

    post_ids = [(k, v) for k, v in post_ids.items()]
    post_ids = sorted(post_ids, key=lambda x: len(x[1]), reverse=True)
    description = f'{redditor} activity for the past 24 hrs'
    embed = Embed(title=redditor, description=description)
    if len(post_ids) == 0:
        return None
    for link in post_ids[:10]:
        try:
            embed.add_field(name=link[1][:200],
                            value=f'https://redd.it/{link[0]}',
                            inline=False)
        except:
            logger.exception('failed to create an embed')
            continue
    return {'embed': embed}


async def hot_pic(subs):
    post = next(subreddit_posts(sub=subs, limit=1, type='hot'))
    return {'content': f'{post.title}\n{post.url}'}


async def top_pic(subs):
    sub = choice(subs.split('+'))
    post = next(subreddit_posts(sub=sub, limit=1, type='top'))
    return {'content': f'{post.title}\n{post.url}'}


if __name__ == '__main__':
    print(asyncio.run(user_track('mbowsy'))['content'])
