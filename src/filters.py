#!/usr/bin/env python

import re

from base import BaseConn


class BaseFilter(BaseConn):
    codename = 'base'
    obj_type = 'filter'
    _params = {}

    def __call__(self, msg):
        if self.filter(msg):
            return True

        return False


class DummyFilter(BaseFilter):
    codename = 'dummy'
    _params = {}

    def filter(self, msg):
        print ('Dummy: %r, %r' % (self.params, msg))

        return True


class FalseFilter(BaseFilter):
    codename = 'false'

    def filter(self, msg):
        return False


class SubjectContainsFilter(BaseFilter):
    codename = 'subject_contains'
    _params = {
        'string': ''
    }

    def filter(self, msg):
        if self.params['string'] in msg['subject']:
            return True


class RegexpMatchesFilter(BaseFilter):
    codename = 'regexp_matches'
    _params = {
        'regexp': '',
        'field': 'subject',
        'flags': [],
    }

    def filter(self, msg):
        val = self.msg_to_dict(msg)[self.params['field']]

        flags = 0

        for flag in self.params['flags']:
            for param in ['i', 'l', 'm', 's', 'u', 'x']:
                if flag == param:
                    flags |= getattr(re, flag.upper())

        try:
            regexp = self.params['regexp'].replace('\\\\', '\\')
            return next(re.finditer(
                regexp,
                val or '',
                flags)) is not None
        except StopIteration:
            return False


def get_filter(name):
    for klass in BaseFilter.__subclasses__():
        if klass.codename == name:
            return klass

    return None
