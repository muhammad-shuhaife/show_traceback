"""Shared URL validation, independent of the ORM."""
import re

PARAM = 'show_traceback.controller_path'
DEFAULT_PATH = '/traceback'
INTERNAL_PATH = '/show_traceback/_current'


def normalize_path(value):
    path = '/' + (value or '').strip().strip('/')
    if not re.fullmatch(r'/[A-Za-z][A-Za-z0-9_-]{0,79}', path):
        raise ValueError('Enter one controller name, such as traceback or /my_error.')
    if path.lower() in {'/odoo', '/web', '/website', '/shop', '/mail', '/discuss',
                        '/report', '/websocket', '/longpolling', '/jsonrpc', '/xmlrpc',
                        '/robots', '/favicon', '/show_traceback'}:
        raise ValueError('This controller name is reserved. Choose another name.')
    return path
