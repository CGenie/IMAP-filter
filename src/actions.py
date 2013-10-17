#1/usr/bin/env python

from base import BaseConn

class BaseAction(BaseConn):
    codename = 'base'
    obj_type = 'action'
    _params = {}

    def __call__(self, msg):
        self.action(msg)


class PrintAction(BaseAction):
    codename = 'print'
    _params = {
        'format': '[%(id)s] %(from)s -- %(subject)s'
    }

    def action(self, msg):
        try:
            msg_dict = self.msg_to_dict(msg)
        except Exception as e:
            print ('ERROR: msg_to_dict failed: %s' % str(e))
            return

        print (self.params['format'] % msg_dict)


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
        'source': 'INBOX',
        'destination': 'INBOX'
    }

    def action(self, msg):
        self.conn.select(self.params['source'])
        self.conn.copy(msg.id, self.params['destination'])


class MoveAction(BaseAction):
    codename = 'move'
    _params = {
        'source': 'INBOX',
        'destination': 'INBOX',
    }

    def action(self, msg):
        self.conn.select(self.params['source'])
        self.conn.copy(msg.id, self.params['destination'])
        self.conn.store(msg.id, "+FLAGS", '(\Deleted)')
        self.conn.expunge()


def get_action(name):
    for klass in BaseAction.__subclasses__():
        if klass.codename == name:
            return klass

    return None
