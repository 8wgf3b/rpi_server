import praw
import os
from functools import partial
from discord import Embed
from random import choice
import logging


logger = logging.getLogger('rpi4.reddit')
reddit = praw.Reddit(client_id= os.environ['CLIENT_ID'],
                     client_secret= os.environ['CLIENT_SECRET'],
                     username= os.environ['USERNAME'],
                     password= os.environ['PASSWORD'],
                     user_agent= os.environ['USER_AGENT'])
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


def random_image_sub(params):
    post = next(subreddit_posts(sub=params, limit=1, type='random'))
    embed = Embed(title=params, description=post.title[:200])
    try:
        embed.set_image(url=post.url)
    except:
        logger.exception('failed to create an embed')
    return {'embed': embed}


def top_day_sub(params):
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


if __name__ == '__main__':
    print(next(subreddit_posts(sub='dankmemes', limit=1, type='random')).title)
