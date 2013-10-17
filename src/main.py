#!/usr/bin/env python

from account import create_connection
from config import read_config



def get_necessary_connections(conf):
    conns = {}

    for plan in conf['plan']:
        for account in plan['accounts']:
            if account in conns:
                continue

            conns[account] = create_connection(
                conf['accounts'][account])


    return conns


class Worker(object):
    def __init__(self, plan=None, conf=None, conns=None):
        self.plan = plan
        self.conf = conf
        self.conns = conns

        self.definition_name = plan['definition']
        self.accounts = plan['accounts']
        self.definition = conf['definitions'][self.definition_name]

    def work(self):
        print ('Working on definition %s' % self.definition_name)

        for account in self.accounts:
            self.account = account

            f = self.definition['fetcher']
            fklass = f['klass']
            if fklass is None:
                continue
            fetcher = fklass(
                self.definition_name,
                self.account,
                conn=self.conns[self.account])
            fetcher.read_params(f.get('params', {}))

            for msg in fetcher():
                fltrs = self.definition['filters']
                if self.all_filters_pass(msg):
                    self.call_actions(msg)

    def all_filters_pass(self, msg):
        for fltr in self.definition['filters']:
            f = fltr['klass']

            if f is None:
                continue

            f = f(
                self.definition_name,
                self.account,
                conn=self.conns[self.account])
            f.read_params(fltr['params'])

            if not f(msg):
                return False

        return True


    def call_actions(self, msg):
        actions = self.definition['actions']

        for action in actions:
            a = action['klass']
            if a is None:
                continue
            a = a(
                self.definition_name,
                self.account,
                conn=self.conns[self.account])
            a.read_params(action['params'])
            a(msg)


def work(conf, conns):
    for i, plan in enumerate(conf['plan']):
        print ('Working on plan %d' % i)

        worker = Worker(plan=plan, conf=conf, conns=conns)
        worker.work()


def close_connections(conns):
    for name, conn in conns.items():
        conn.logout()


if __name__ == '__main__':
    conf = read_config()
    print ('Configuration: %r' % conf)

    conns = get_necessary_connections(conf)

    work(conf, conns)

    close_connections(conns)
