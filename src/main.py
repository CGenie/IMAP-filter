#!/usr/bin/env python

from account import create_connection
from config import read_config


def get_necessary_connections(conf):
    conns = {}

    for name, definition in conf['definitions'].items():
        for account in definition['accounts']:
            if account in conns:
                continue

            conns[account] = create_connection(
                conf['accounts'][account])


    return conns


def all_filters_pass(msg, filters, conn):
    for fltr in filters:
        f = fltr['klass']
        if f is None:
            continue
        f = f(conn=conn)
        f.read_params(fltr['params'])
        if not f(msg):
            return False

    return True


def call_actions(msg, actions, conn):
    for action in actions:
        a = action['klass']
        if a is None:
            continue
        a = a(conn=conn)
        a.read_params(action['params'])
        a(msg)


def work(conf, conns):
    for name, definition in conf['definitions'].items():
        print 'Working on definition %s' % name
        for account in definition['accounts']:
            conn = conns[account]
            f = definition['fetcher']
            fetcher = f['klass'](conn=conn)
            fetcher.read_params(f.get('params', {}))
            for msg in fetcher():
                fltrs = definition['filters']
                if all_filters_pass(msg, fltrs, conn):
                    actions = definition['actions']
                    call_actions(msg, actions, conn)


def close_connections(conns):
    for name, conn in conns.items():
        conn.logout()


if __name__ == '__main__':
    conf = read_config()
    print 'Configuration: %r' % conf

    conns = get_necessary_connections(conf)

    work(conf, conns)

    close_connections(conns)
