"""One complete current error per database, shared by local Odoo workers."""
import hashlib
import json
import os
import tempfile

from odoo.tools import config


def _path(db):
    digest = hashlib.sha256(db.encode('utf-8')).hexdigest()
    return os.path.join(config['data_dir'], 'show_traceback_current', digest + '.json')


def replace(db, record):
    if not db:
        return
    path = _path(db)
    directory = os.path.dirname(path)
    os.makedirs(directory, mode=0o700, exist_ok=True)
    fd, temporary = tempfile.mkstemp(dir=directory, prefix='.current-')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            json.dump(record, stream)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def current(db):
    if not db:
        return None
    try:
        with open(_path(db), encoding='utf-8') as stream:
            return json.load(stream)
    except (FileNotFoundError, ValueError):
        return None


def _config_path(db):
    return _path(db) + '.endpoint'


def configuration(db):
    try:
        with open(_config_path(db), encoding='utf-8') as stream:
            return json.load(stream)
    except (OSError, ValueError):
        return None


def configure(db, path, grant):
    import fcntl
    import time
    filename = _config_path(db)
    directory = os.path.dirname(filename)
    os.makedirs(directory, mode=0o700, exist_ok=True)
    lock = os.open(filename + '.lock', os.O_CREAT | os.O_RDWR, 0o600)
    try:
        fcntl.flock(lock, fcntl.LOCK_EX)
        old = configuration(db) or {}
        grants = [g for g in old.get('grants', []) if g['expires'] > time.time()
                  and g['session'] != grant['session']]
        value = {'db': db, 'path': path, 'grants': (grants + [grant])[-10:]}
        fd, temporary = tempfile.mkstemp(dir=directory, prefix='.endpoint-')
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as stream:
                json.dump(value, stream)
            os.replace(temporary, filename)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
    finally:
        os.close(lock)


def configurations_for(path):
    import glob
    directory = os.path.dirname(_path(''))
    out = []
    for filename in glob.glob(os.path.join(directory, '*.json.endpoint')):
        try:
            with open(filename, encoding='utf-8') as stream:
                value = json.load(stream)
            if value['path'] == path:
                out.append(value)
        except (OSError, ValueError, KeyError, TypeError):
            continue
    return out
