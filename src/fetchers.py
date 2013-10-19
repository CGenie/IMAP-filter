#!/usr/bin/env python

import email
import re

from base import BaseConn


class BaseFetcher(BaseConn):
    codename = 'base'
    obj_type = 'fetcher'
    _params = {}

    def __init__(self, *args, **kwargs):
        super(BaseFetcher, self).__init__(*args, **kwargs)

        self.uid_re = re.compile('\d+ \(UID (?P<uid>\d+)\)')

    def __call__(self):
        for msg in self.fetch():
            yield msg

    def fetch_uid(self, num):
        msg_uid = self.conn.fetch(num, '(UID)')
        return self.uid_re.match(msg_uid[1][0].decode('utf-8')).group('uid')

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

            ret.uid = self.fetch_uid(num)

            return ret

    def fetch_directory_uids(self, directory):
        num_emails = self.conn.select(directory, readonly=True)
        num_emails = int(num_emails[1][0])

        msg_id = int(msg_id)

        for i in range(num_emails):
            yield {
                'uid': int(self.fetch_uid()),
                'id': i
            }

    def fetch_latest(self, directory, max_num=15):
        num_emails = self.conn.select(directory, readonly=True)
        num_emails = int(num_emails[1][0])

        uids = list(self.fetch_directory_uids(directory))

        uids.sort(lambda d: d['uid'])

        #typ, data = self.conn.search(None, 'ALL')
        #typ, data = self.conn.sort('REVERSE DATE', 'UTF-8', 'ALL')

        for d in uids[:-max_num]:
            msg = self.fetch_email(str(d['id']), directory)

            if msg is not None:
                yield msg

    def fetch_from_msg_id(self, directory, msg_id):
        num_emails = self.conn.select(directory, readonly=True)
        num_emails = int(num_emails[1][0])

        msg_id = int(msg_id)

        for i in range(num_emails):
            uid = int(self.fetch_uid())
            if uid >= msg_id:
                msg = self.fetch_email(str(i), directory)

                if msg is None:
                    continue

                yield msg
#
#        for i in range(msg_id, num_emails):
#            msg = self.fetch_email(str(i), directory)
#
#            if msg is None:
#                continue
#
#            yield msg


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
