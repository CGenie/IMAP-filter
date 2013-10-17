#!/usr/bin/env python

import email

from base import BaseConn


class BaseFetcher(BaseConn):
    codename = 'base'
    obj_type = 'fetcher'
    _params = {}

    def __call__(self):
        for msg in self.fetch():
            yield msg

    def fetch_email(self, num, directory):
        self.conn.select(directory, readonly=True)

        typ, data = self.conn.fetch(num, '(RFC822)')

        response_part = data[0]
        if isinstance(response_part, tuple):
            s = response_part[1]
            if isinstance(s, bytes):
                ret = email.message_from_bytes(s)
            else:
                ret = email.message_from_string(s)

            ret.id = num

            return ret

    def fetch_latest(self, directory, max_num=15):
        self.conn.select(directory, readonly=True)

        typ, data = self.conn.search(None, 'ALL')
        ids = data[0]
        id_list = ids.split()
        latest_email_id = int(id_list[-max_num])

        for msg in self.fetch_from_msg_id(directory, latest_email_id):
            if msg is None:
                continue

            yield msg

    def fetch_from_msg_id(self, directory, msg_id):
        self.conn.select(directory, readonly=True)

        typ, data = self.conn.search(None, 'ALL')
        ids = data[0]
        id_list = ids.split()

        for i in id_list:
            if int(i) < msg_id:
                continue

            msg = self.fetch_email(i, 'INBOX')

            if msg is None:
                continue

            yield msg


class GetLatestFetcher(BaseFetcher):
    codename = 'get_latest'
    _params = {
        'directory': 'INBOX',
        'num_emails': 15,
    }

    def fetch(self):
        state = self.state

        for msg in self.fetch_latest(
                self.params['directory'],
                max_num=self.params['num_emails']):
            if msg is not None:
                yield msg


class StateFetcher(BaseFetcher):
    codename = 'incremental'
    _params = {
        'directory': 'INBOX',
    }

    def fetch(self):
        state = self.state
        latest_msg_id = state.get('latest_msg_id', 0)

        for msg in self.fetch_from_msg_id(
                self.params['directory'],
                latest_msg_id):

            if msg is None:
                continue

            yield msg

            state['latest_msg_id'] = int(msg.id)
            self.save_state(state)


def get_fetcher(name):
    for klass in BaseFetcher.__subclasses__():
        if klass.codename == name:
            return klass

    return None
