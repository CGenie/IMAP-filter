#!/usr/bin/env python


class BaseConn(object):
    codename = 'base'
    _params = {}

    def __init__(self, conn=None):
        self.conn = conn

    def read_params(self, params):
        self.params = self._params.copy()
        self.params.update(params)

    def msg_to_dict(self, msg):
        return {
            'subject': msg['subject'],
            'from': msg['from'],
            'body': self.get_msg_payload(msg),
        }

    def get_msg_payload(self, msg):
        maintype = msg.get_content_maintype()

        if maintype == 'multipart':
            return ''.join([
                self.get_msg_payload(part) for part in msg.get_payload()])

        elif maintype == 'text':
            return msg.get_payload()

        return ''
