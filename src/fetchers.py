#!/usr/bin/env python

import email

from base import BaseConn


class BaseFetcher(BaseConn):
    codename = 'base'
    _params = {}

    def __call__(self):
        for msg in self.fetch():
            yield msg

    def fetch_email(self, num, directory):
        self.conn.select(directory)

        typ, data = self.conn.fetch(num, '(RFC822)')

        response_part = data[0]
        if isinstance(response_part, tuple):
            ret = email.message_from_string(response_part[1])

            ret.id = num

            return ret

    def fetch_latest(self, directory, max_num=15):
        self.conn.select(directory)

        typ, data = self.conn.search(None, 'ALL')
        ids = data[0]
        id_list = ids.split()
        latest_email_id = int(id_list[-1])

        for i in range(
                latest_email_id,
                latest_email_id - max_num,
                -1):
            msg = self.fetch_email(i, 'INBOX')

            yield msg


class GetLatestFetcher(BaseFetcher):
    codename = 'get_latest'
    _params = {
        'directory': 'INBOX',
        'num_emails': 15
    }

    def fetch(self):
        for msg in self.fetch_latest(
                self.params['directory'],
                max_num=self.params['num_emails']):
            yield msg


def get_fetcher(name):
    for klass in BaseFetcher.__subclasses__():
        if klass.codename == name:
            return klass

    return None
