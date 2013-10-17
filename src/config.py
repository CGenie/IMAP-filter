#!/usr/bin/env python

import json
import os

from base import config_file
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
        'name': name,
        'fetcher': None,
        'filters': [],
        'actions': [],
    }

    ret[name]['fetcher'] = parse_fetcher(definition.get('fetcher', {}))
    for fltr in definition.get('filters', []):
        ret[name]['filters'].append(parse_filter(fltr))
    for action in definition.get('actions', []):
        ret[name]['actions'].append(parse_action(action))


def parse_plan(plan, ret):
    ret.append(plan)


def read_config():
    """Create base directories and read config file."""
    ret = {
        'accounts': {},
        'definitions': {},
        'plan': [],
    }

    conf = config_file('config.json')

    with open(conf) as f:
        config = json.loads(f.read())
        for name, account in config.get('accounts', {}).items():
            parse_account(name, account, ret['accounts'])

        for name, definition in config.get('definitions', {}).items():
            parse_definition(name, definition, ret['definitions'])

        for plan in config.get('plan', []):
            parse_plan(plan, ret['plan'])
        
    return ret
