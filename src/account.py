#!/usr/bin/env python

import imaplib


def create_connection(account):
    params = [
        account['server'],
        account['port'],
    ]

    if account['tls']:
        conn = imaplib.IMAP4_SSL(*params)
    else:
        conn = imaplib.IMAP4(*params)

    conn.login(account['login'], account['password'])

    return conn
