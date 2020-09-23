import aiohttp
import asyncio
from discord import Embed
from collections import defaultdict
from itertools import chain
import logging
from pprint import pprint, pformat
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd


logger = logging.getLogger('rpi4.reddit')

SMALL_SIZE = 6
MEDIUM_SIZE = 8
BIGGER_SIZE = 10


async def get_user_data(user):
    time_agg = defaultdict(lambda: 0)

    params = {'author': user, 'size': 0}
    params['aggs'] = ','.join(['subreddit', 'created_utc'])
    params['frequency'] ='hour'
    params['after'] = '30d'

    sub_df = defaultdict(lambda: {'p_30': 0, 'c_30': 0, 'p_all': 0, 'c_all': 0})
    # last 30 days
    logger.debug('fetching last 30 days stats')
    pdata = await pushshift_fetcher('post', params)
    cdata = await pushshift_fetcher('comment', params)
    logger.info('fetched last 40 days stats')

    for i in pdata['aggs']['subreddit']:
        sub_df[i['key']]['p_30'] = i['doc_count']
    for i in cdata['aggs']['subreddit']:
        sub_df[i['key']]['c_30'] = i['doc_count']

    time_data = chain(pdata['aggs']['created_utc'], cdata['aggs']['created_utc'])
    for i in time_data:
        time_agg[i['key']] += i['doc_count']
    time_df = pd.DataFrame(time_agg.items(), columns=['time', 'activity'])
    time_df['time'] = pd.to_datetime(time_df['time'], unit='s')
    time_df['Date'] = time_df['time'].apply(lambda x: str(x).split(" ")[0])
    time_df['Hour'] = time_df['time'].apply(lambda x: str(x).split(" ")[1].split(":")[0])
    pv = pd.pivot_table(time_df, values='activity', index='Hour', columns='Date').fillna(0)   

    # lifetime
    del params['after']
    del params['frequency']
    params['aggs'] = 'subreddit'

    logger.debug('fetching lifetime stats')
    pdata = await pushshift_fetcher('post', params)
    cdata = await pushshift_fetcher('comment', params)
    logger.info('fetched lifetime stats')

    for i in pdata['aggs']['subreddit']:
        sub_df[i['key']]['p_all'] = i['doc_count']
    for i in cdata['aggs']['subreddit']:
        sub_df[i['key']]['c_all'] = i['doc_count']

    sub_df = pd.DataFrame(data=sub_df.values(), index=sub_df.keys())

    return pv, sub_df


async def pushshift_fetcher(endpoint, params):
    logger.info(f'fetching from pushshift {endpoint} with these params: {pformat(params)}')
    if endpoint == 'comment':
        url = "https://api.pushshift.io/reddit/search/comment/"
    elif endpoint == 'post':
        url = "https://api.pushshift.io/reddit/search/submission/"
    else:
        logger.error(f'Wrong endpoint {endpoint}')
        raise ValueError('Wrong value for endpoint argument')
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as r:
                return await r.json()
    except Exception:
        logger.exception('decode error?')
        return None


async def make_user_report(username, location='temp/lol.png'):
    time_stats, sub_stats = await get_user_data(username)

    fig, axes = plt.subplots(nrows=3, ncols=2, figsize=(10,10))

    # set text sizes
    plt.rc('font', size=SMALL_SIZE)
    plt.rc('axes', titlesize=MEDIUM_SIZE)
    plt.rc('axes', labelsize=MEDIUM_SIZE)
    plt.rc('xtick', labelsize=SMALL_SIZE)
    plt.rc('ytick', labelsize=SMALL_SIZE)
    plt.rc('legend', fontsize=MEDIUM_SIZE)
    plt.rc('figure', titlesize=MEDIUM_SIZE)

    # sub aggregations plots
    sub_stats.sort_values(['p_30'],ascending = False).head(10)[['p_30']].plot.barh(legend = False, ax = axes[0,0])
    axes[0,0].set_title('last 30 days posts')

    sub_stats.sort_values(['p_all'],ascending = False).head(10)[['p_all']].plot.barh(legend = False, ax = axes[0,1])
    axes[0,1].set_title('lifetime posts')
    
    sub_stats.sort_values(['c_30'],ascending = False).head(10)[['c_30']].plot.barh(legend = False, ax = axes[1,0])
    axes[1,0].set_title('last 30 days comments')

    sub_stats.sort_values(['c_all'],ascending = False).head(10)[['c_all']].plot.barh(legend = False, ax = axes[1,1])
    axes[1,1].set_title('lifetime comments')
    
    sns.heatmap(time_stats, cmap = sns.cm.rocket_r, ax = axes[2, 0])
    axes[2, 0].set_title('latest activity (utc)')    
    
    plt.tight_layout()
    plt.savefig(location, dpi = 100)          



if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(make_user_report('quoiega', 'lol.png'))
    # pprint(user_info)
