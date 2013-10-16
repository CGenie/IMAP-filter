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


def get_action(name):
    for klass in BaseAction.__subclasses__():
        if klass.codename == name:
            return klass

    return None
