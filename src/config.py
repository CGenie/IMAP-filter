#!/usr/bin/env python

import json
import os

from actions import get_action
from filters import get_filter
from fetchers import get_fetcher


def parse_account(name, config, ret):
    ret[name] = {
        'login': '',
        'password': '',
        'server': '',
        'port': 143,
        'tls': False
    }

    ret[name].update(config)

    return ret


def parse_fetcher(fetcher):
    ret = {
        'klass': None,
        'params': {},
    }

    ret['klass'] = get_fetcher(fetcher.get('type', 'get_latest'))
    ret['params'] = fetcher.get('params', {})

    return ret


def parse_filter(fltr):
    ret = {
        'klass': None,
        'params': {},
    }

    ret['klass'] = get_filter(fltr.get('filter', 'dummy'))
    ret['params'] = fltr.get('params', {})

    return ret


def parse_action(action):
    ret = {
        'klass': None,
        'params': {},
    }

    ret['klass'] = get_action(action.get('action', 'print'))
    ret['params'] = action.get('params', {})

    return ret


def parse_definition(name, definition, ret):
    ret[name] = {
        'accounts': [],
        'fetcher': None,
        'filters': [],
        'actions': [],
    }

    ret[name]['accounts'] = definition.get('accounts', [])
    ret[name]['fetcher'] = parse_fetcher(definition.get('fetcher', {}))
    for fltr in definition.get('filters', []):
        ret[name]['filters'].append(parse_filter(fltr))
    for action in definition.get('actions', []):
        ret[name]['actions'].append(parse_action(action))


def read_config():
    """Create base directories and read config file."""
    ret = {
        'accounts': {},
        'definitions': {},
    }

    home = os.environ['HOME']
    d = os.path.join(home, '.IMAP-filter')

    if not os.path.exists(d):
        os.makedirs(d)

    conf = os.path.join(d, 'config.json')

    if not os.path.exists(conf):
        with open(conf, 'a') as f:
            f.write('{}\n')

    with open(conf) as f:
        config = json.loads(f.read())
        for name, account in config.get('accounts', {}).items():
            parse_account(name, account, ret['accounts'])

        for name, definition in config.get('definitions', {}).items():
            parse_definition(name, definition, ret['definitions'])
        
    return ret
