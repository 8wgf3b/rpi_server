from sqlalchemy import (Table, Column, String, Integer, DateTime,
                        Boolean, MetaData, create_engine,
                        insert, select, update, delete, and_)
from datetime import datetime
from croniter import croniter


def get_next_run(cron_exp, base):
    return croniter(cron_exp, base).get_next(datetime)


engine = create_engine('sqlite:///databases/bot.db')
connection = engine.connect()
metadata = MetaData()

Tasks = Table('Tasks', metadata,
              Column('id', Integer(), primary_key=True),
              Column('channel_id', String(50), nullable=False),
              Column('cron_exp', String(20), nullable=False),
              Column('next_run', DateTime, default=datetime.utcnow()),
              Column('func', String(20), nullable=False),
              Column('params', String(100)))

metadata.create_all(engine)


def create_new_task(channel_id, cron_exp, func, params):
    del_stmt = delete(Tasks).where(and_(Tasks.columns.channel_id == channel_id,
                                        Tasks.columns.cron_exp == cron_exp,
                                        Tasks.columns.func == func,
                                        Tasks.columns.params == params))
    del_res = connection.execute(del_stmt)
    stmt = insert(Tasks).values(channel_id=channel_id, cron_exp=cron_exp,
                                func=func, params=params)
    result_proxy = connection.execute(stmt)
    return result_proxy.rowcount


def fetch_update_to_be_run(base):
    stmt = select([Tasks])
    stmt = stmt.where(Tasks.columns.next_run <= base)
    results = connection.execute(stmt).fetchall()
    if len(results) != 0:
        stmt = delete(Tasks).where(Tasks.columns.next_run <= base)
        delete_proxy = connection.execute(stmt)
        keys = ['channel_id', 'cron_exp', 'next_run', 'func', 'params']
        updated = [dict(zip(keys, result[1:])) for result in results]
        for d in updated:
            d['next_run'] = get_next_run(d['cron_exp'], base)
        stmt = insert(Tasks)
        insert_proxy = connection.execute(stmt, updated)
    return results


def update_next_run(base):
    stmt = update(Tasks)
    stmt = stmt.where(Tasks.columns.next_run <= base)
    stmt = stmt.values(next_run=get_next_run(Tasks.columns.cron_exp, base))
    result_proxy = connection.execute(stmt)
    return result_proxy


def clear_channel_tasks(cid):
    stmt = delete(Tasks).where(Tasks.columns.channel_id == cid)
    delete_proxy = connection.execute(stmt)
    return delete_proxy.rowcount


def delete_by_ids(ids):
    if not isinstance(ids, list):
        ids = [ids]
    stmt = delete(Tasks).where(Tasks.columns.id.in_(ids))
    delete_proxy = connection.execute(stmt)
    return delete_proxy.rowcount


def fetch_channel_tasks(cid):
    stmt = select([Tasks]).where(Tasks.columns.channel_id == cid)
    return connection.execute(stmt).fetchall()


def pretty_channel_tasks(cid):
    results = fetch_channel_tasks(cid)
    fin_s = ['Channel\'s scheduled tasks']
    for result in results:
        s = f'{result.id} {result.cron_exp} {result.func} {result.params}'
        fin_s.append(s)
    text = '\n'.join(fin_s)
    if not text:
        text = 'Nothing scheduled yet :)'
    return text


def fetch_all_tasks():
    stmt = select([Tasks])
    return connection.execute(stmt).fetchall()


if __name__ == '__main__':
    base = datetime.utcnow()
    create_new_task('a', '* * * * *', 'b', 'c')
    print(fetch_update_to_be_run(base))
