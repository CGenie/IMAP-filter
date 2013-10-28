#!/usr/bin/env python

from email import header
import json
import os


def config_dir():
    home = os.environ['HOME']
    d = os.path.join(home, '.IMAP-filter')

    if not os.path.exists(d):
        os.makedirs(d)

    return d


def config_file(f):
    conf = os.path.join(config_dir(), f)

    if not os.path.exists(conf):
        with open(conf, 'a') as f:
            f.write('{}\n')

    return conf


class StatePreserver(object):
    codename = 'base'
    obj_type = 'state'

    def __init__(self, definition_name, account_name, *args, **kwargs):
        self.state_file = config_file('%s.json' % self.obj_type)
        self.definition_name = definition_name
        self.account_name = account_name

    @property
    def state(self):
        ret = {}

        with open(self.state_file, 'r') as f:
            r = json.loads(f.read() or '{}')
            ret = r.get(self.definition_name, {})

            ret = ret.get(self.account_name, {})

            ret = ret.get(self.codename, {})

        return ret

    def save_state(self, state):
        with open(self.state_file, 'r') as f:
            r = json.loads(f.read() or '{}')

        with open(self.state_file, 'w') as f:
            r.setdefault(self.definition_name, {})
            defi = r[self.definition_name]
            defi.setdefault(self.account_name, {})

            act = defi[self.account_name]
            act.setdefault(self.codename, {})
            act[self.codename].update(state)

            f.write(json.dumps(r, indent=4))


class BaseConn(StatePreserver):
    codename = 'base'
    obj_type = 'conn'
    _params = {}

    def __init__(self, *args, **kwargs):
        conn = kwargs.pop('conn', None)

        super(BaseConn, self).__init__(*args, **kwargs)

        self.conn = conn

    def read_params(self, params):
        self.params = self._params.copy()
        self.params.update(params)

    def _header_convert(self, txt, encoding=None):
        if encoding is None:
            encoding = 'utf-8'

        if isinstance(txt, header.Header):
            txt = txt.encode(encoding)
        elif isinstance(txt, tuple):
            txt = self._header_convert(txt[0], encoding=txt[1])
        elif isinstance(txt, list):
            txt = ' '.join(self._header_convert(l) for l in txt)
        elif isinstance(txt, bytes):
            txt = txt.decode(encoding)

        return txt

    def msg_to_dict(self, msg):
        subject = self._header_convert(header.decode_header(msg['subject']))
        fro = self._header_convert(header.decode_header(msg['from']))
        to = self._header_convert(header.decode_header(msg['to']))

        return {
            'id': int(msg.id),
            'subject': subject,
            'from': fro,
            'to': to,
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
