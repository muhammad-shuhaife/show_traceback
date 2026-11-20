"""Database-free viewer after normal addon loading; no server-wide module required."""
import hashlib
import hmac
import logging
import secrets
import time
import traceback
from datetime import datetime, timezone
from functools import wraps

from odoo import http
from odoo.exceptions import AccessDenied, AccessError, UserError
from werkzeug.wrappers import Request, Response

from . import store
from .compat import Application, SessionExpiredException
from .page import render_page, HEADERS

_logger = logging.getLogger(__name__)
GRANT_SECONDS = 8 * 60 * 60


def cookie_name(db):
    return 'odoo_traceback_' + hashlib.sha256(db.encode()).hexdigest()[:16]


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


def authorize_browser(request, path):
    """Call only after checking the current user's Settings administrator rights."""
    db = request.db
    token = secrets.token_urlsafe(32)
    session_id = request.session.sid
    grant = {'token': digest(token), 'session': digest(session_id),
             'expires': time.time() + GRANT_SECONDS}
    # Commit the endpoint only if the associated Settings transaction commits.
    request.env.cr.postcommit.add(lambda: store.configure(db, path, grant))
    request.future_response.set_cookie(
        cookie_name(db), token, max_age=GRANT_SECONDS, path='/',
        httponly=True, samesite='Strict', secure=request.httprequest.scheme == 'https')


def authorized(config, request):
    # This separate short-lived capability must survive Odoo logging out or
    # rotating its session as a side effect of a registry failure.
    # It was issued only after a successful Settings-administrator check.
    token = request.cookies.get(cookie_name(config['db']), '')
    if not token:
        return False
    return any(g['expires'] > time.time()
               and hmac.compare_digest(g['token'], digest(token))
               for g in config.get('grants', []))


def capture(exc, exc_info=None):
    """Capture without ORM access: the request cursor may already be broken."""
    if isinstance(exc, (UserError, AccessError, AccessDenied, SessionExpiredException)):
        return
    from werkzeug.exceptions import HTTPException
    if isinstance(exc, HTTPException) and (exc.code is None or exc.code < 500):
        return
    if getattr(exc, '_show_traceback_saved', False):
        return
    try:
        request = http.request
        db = getattr(request, 'db', None) or getattr(request.session, 'db', None)
        if not db:
            return
        configuration = store.configuration(db)
        path = request.httprequest.path
        if path.startswith('/show_traceback/') or (
                configuration and path.rstrip('/') == configuration['path']):
            return  # Never replace the useful error with a viewer failure.
        details = exc_info or (type(exc), exc, exc.__traceback__)
        store.replace(db, {
            'time': datetime.now(timezone.utc).isoformat(),
            'method': request.httprequest.method, 'path': path,
            'error_type': type(exc).__name__, 'message': str(exc),
            'traceback': ''.join(traceback.format_exception(*details)),
        })
        exc._show_traceback_saved = True
    except Exception:
        _logger.exception('Could not save the current error traceback')


class RequestErrors(logging.Handler):
    def emit(self, record):
        if not record.exc_info or not record.exc_info[1]:
            return
        if record.levelno < logging.ERROR and not str(record.msg).startswith('Database or registry unusable'):
            return
        # Only configured databases are monitored by this process-wide fallback.
        try:
            request = http.request
            db = getattr(request, 'db', None) or getattr(request.session, 'db', None)
            if db and store.configuration(db):
                capture(record.exc_info[1], record.exc_info)
        except Exception:
            pass


def install():
    original = Application.__call__
    if getattr(original, '_show_traceback_emergency', False):
        return

    @wraps(original)
    def application(self, environ, start_response):
        path = environ.get('PATH_INFO', '').rstrip('/')
        configurations = store.configurations_for(path)
        if configurations:
            request = Request(environ)
            matching = [c for c in configurations if authorized(c, request)]
            if matching:
                # A browser may use multiple DBs sharing a URL. Never pick one arbitrarily.
                selected = request.args.get('db')
                if selected:
                    matching = [c for c in matching if c['db'] == selected]
                if len(matching) != 1:
                    response = Response('Select the database using ?db=DATABASE_NAME.', status=400, headers=HEADERS)
                elif request.method not in ('GET', 'HEAD'):
                    response = Response('Method Not Allowed', status=405,
                                        headers={**HEADERS, 'Allow': 'GET, HEAD'})
                else:
                    try:
                        response = Response(render_page(store.current(matching[0]['db'])),
                                            content_type='text/html; charset=utf-8', headers=HEADERS)
                    except (OSError, ValueError, TypeError, KeyError):
                        response = Response('The saved traceback cannot be read. Check the Odoo data directory permissions.',
                                            status=503, headers=HEADERS)
                return response(environ, start_response)
            # A healthy Odoo can authenticate and grant access to another browser.
            # With a broken registry, an existing emergency grant is required.
            return original(self, environ, start_response)
        return original(self, environ, start_response)

    application._show_traceback_emergency = True
    Application.__call__ = application
    handler = RequestErrors(level=logging.WARNING)
    logging.getLogger('odoo.http').addHandler(handler)
