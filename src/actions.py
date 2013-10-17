#1/usr/bin/env python

from base import BaseConn

class BaseAction(BaseConn):
    codename = 'base'
    _params = {}

    def __call__(self, msg):
        self.action(msg)


class PrintAction(BaseAction):
    codename = 'print'
    _params = {
        'format': '%(from)s -- %(subject)s'
    }

    def action(self, msg):
        print self.params['format'] % msg


class WriteToFileAction(BaseAction):
    codename = 'write_to_file'
    _params = {
        'file': 'out.txt',
        'format': '%(from)s -- %(subject)s\n'
    }

    def action(self, msg):
        with open(self.params['file'], 'a') as f:
            f.write(self.params['format'] % self.msg_to_dict(msg))


class CopyAction(BaseAction):
    codename = 'copy'
    _params = {
        'destination': 'INBOX'
    }

    def action(self, msg):
        self.conn.copy(msg.id, self.params['destination'])


class MoveAction(BaseAction):
    codename = 'move'
    _params = {
        'destination': 'INBOX'
    }

    def action(self, msg):
        self.conn.copy(msg.id, self.params['destination'])
        self.conn.store(msg.id, "+FLAGS", '(\Deleted)')
        self.conn.expunge()


def get_action(name):
    for klass in BaseAction.__subclasses__():
        if klass.codename == name:
            return klass

    return None
